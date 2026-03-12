from django.shortcuts import render
from .models import Course
from .serializers import CoureSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from accounts.permissions import IsSuperAdmin, IsInstructor, IsOrgAdmin, IsStudent

# Create your views here.


class CouserViewset(viewsets.ModelViewSet):
    serializer_class = CoureSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        if user.role == "SUPERADMIN":
            return Course.objects.all()
        return Course.objects.filter(institute__organization=user.organization)
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        elif self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, (IsInstructor)] 
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(instructor= self.request.user)
    
    
    
    
