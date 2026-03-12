from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id", "enrollment", "amount",
            "status", "stripe_payment_intent",
            "paid_at", "created_at",
        ]
        read_only_fields = [
            "status", "stripe_payment_intent",
            "paid_at", "created_at",
        ]


class CreateCheckoutSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()