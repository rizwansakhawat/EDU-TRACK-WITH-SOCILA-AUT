from rest_framework import serializers
from .models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="enrollment.student.get_full_name", read_only=True)
    course_name = serializers.CharField(source="enrollment.course.title", read_only=True)
    instructor_name = serializers.CharField(source="enrollment.course.instructor.get_full_name", read_only=True)
    completion_date = serializers.DateTimeField(source="enrollment.completed_at", read_only=True)

    class Meta:
        model = Certificate
        fields = [
            "id", "certificate_id", "enrollment",
            "student_name", "course_name", "instructor_name",
            "completion_date", "issued_at",
        ]