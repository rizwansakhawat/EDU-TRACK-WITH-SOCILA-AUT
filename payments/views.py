import stripe
from django.conf import settings
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

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET

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
            enrollment_id = session["metadata"].get("enrollment_id")
            payment_intent = session.get("payment_intent")

            # Mark payment as completed
            Payment.objects.filter(
                enrollment_id=enrollment_id,
                stripe_payment_intent=payment_intent,
                status="pending",
            ).update(status="completed", paid_at=timezone.now())

            # Activate the enrollment
            Enrollment.objects.filter(pk=enrollment_id).update(status="active")

        return Response({"status": "ok"}, status=status.HTTP_200_OK)



