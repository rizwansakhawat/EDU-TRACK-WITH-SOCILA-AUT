from rest_framework import serializers
from .models import Enrollment, Payment


class EnrollmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Enrollment
        fields = "__all__"
        read_only_fields = ["student"]
         
    def validate(self, data):
        student = self.context["request"].user
        course = data["course"]
        if Enrollment.objects.filter(student=student, course=course).exists():
            raise serializers.ValidationError(
                "You are already enrolled in this course.")
        return data
    
    
class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = "__all__"
