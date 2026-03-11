from django.shortcuts import render
from rest_framework import viewsets
from .serializers import CertificateSerializer
from .models import Certificate
from rest_framework.permissions import IsAuthenticated

# Create your views here.


class CertificateViewSet(viewsets.ModelViewSet):
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "STUDENT":
            return Certificate.objects.filter(enrollment__student=user)

        return Certificate.objects.filter(
            enrollment__course__institute__organization=user.organization)