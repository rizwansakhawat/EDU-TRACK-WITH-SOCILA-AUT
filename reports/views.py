from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .serializers import CertificateSerializer
from .models import Certificate


class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only: certificates are auto-generated on course completion."""
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "STUDENT":
            return Certificate.objects.filter(enrollment__student=user)

        return Certificate.objects.filter(
            enrollment__course__institute__organization=user.organization)