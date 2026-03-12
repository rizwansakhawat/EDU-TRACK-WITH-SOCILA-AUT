from django.shortcuts import render
from rest_framework import viewsets
from .serializers import EnrollmentSerializer
from .models import Enrollment
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from accounts.permissions import IsStudent, IsSuperAdmin, IsInstructor, IsOrgAdmin

# Create your views here.


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "STUDENT":
            return Enrollment.objects.filter(student=user)

        return Enrollment.objects.filter(
            course__institute__organization=user.organization
        )
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsStudent]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]
    

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
        

