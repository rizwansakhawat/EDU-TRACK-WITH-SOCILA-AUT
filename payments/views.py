import stripe
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course
from enrollments.models import Enrollment
from reports.models import Certificate
from .models import Payment
from .serializers import PaymentSerializer, CreateCheckoutSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """List / retrieve payments for the authenticated user."""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(enrollment__student=self.request.user)


class CreateCheckoutSession(APIView):
    """
    Create a Stripe Checkout Session for a course.
    Returns the checkout URL so the client can redirect the user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateCheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course_id = serializer.validated_data["course_id"]
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get or create a pending enrollment
        enrollment, _ = Enrollment.objects.get_or_create(
            student=request.user,
            course=course,
            defaults={"status": "active"},
        )

        # Prevent duplicate payments
        if Payment.objects.filter(enrollment=enrollment, status="completed").exists():
            return Response(
                {"detail": "You have already paid for this course."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": course.title},
                        "unit_amount": int(course.price * 100),  # cents
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            metadata={
                "enrollment_id": str(enrollment.id),
                "user_id": str(request.user.id),
            },
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
        )

        # Record a pending payment
        Payment.objects.create(
            enrollment=enrollment,
            amount=course.price,
            stripe_payment_intent=checkout_session.payment_intent,
            status="pending",
        )

        return Response(
            {"checkout_url": checkout_session.url},
            status=status.HTTP_201_CREATED,
        )



@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    """
    Handle Stripe webhook events (e.g. checkout.session.completed).
    Stripe sends a POST with the event payload; we verify the signature,
    mark the payment as completed, and auto-generate a certificate.
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response(
            {
                "detail": "Stripe webhook endpoint is reachable. Stripe should send POST requests here.",
                "status": "ready",
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET

        if not webhook_secret:
            return Response(
                {"detail": "Stripe webhook secret is not configured."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            return Response(
                {"detail": "Invalid signature."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            enrollment_id = session.get("metadata", {}).get("enrollment_id")
            payment_intent = session.get("payment_intent")

            if not enrollment_id:
                return Response({"status": "ok"}, status=status.HTTP_200_OK)

            with transaction.atomic():
                pending_qs = Payment.objects.select_for_update().filter(
                    enrollment_id=enrollment_id,
                    status="pending",
                )

                payment = None

                if payment_intent:
                    payment = pending_qs.filter(
                        stripe_payment_intent=payment_intent
                    ).order_by("-created_at").first()

                if payment is None:
                    payment = pending_qs.filter(
                        stripe_payment_intent__isnull=True
                    ).order_by("-created_at").first()

                if payment is None:
                    payment = pending_qs.order_by("-created_at").first()

                if payment:
                    payment.status = "completed"
                    payment.paid_at = timezone.now()
                    if payment_intent and not payment.stripe_payment_intent:
                        payment.stripe_payment_intent = payment_intent
                    payment.save(
                        update_fields=["status", "paid_at", "stripe_payment_intent"]
                    )

                Enrollment.objects.filter(pk=enrollment_id).update(status="active")
                Certificate.objects.get_or_create(enrollment_id=enrollment_id)

        return Response({"status": "ok"}, status=status.HTTP_200_OK)





class PaymentSuccessView(APIView):
    """User-facing success endpoint for Stripe Checkout redirect."""
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response(
            {
                "detail": "Payment flow completed. Verification is handled by Stripe webhook.",
                "status": "success",
            },
            status=status.HTTP_200_OK,
        )


class PaymentCancelView(APIView):
    """User-facing cancel endpoint for Stripe Checkout redirect."""
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response(
            {
                "detail": "Payment was canceled. You can retry checkout.",
                "status": "canceled",
            },
            status=status.HTTP_200_OK,
        )



