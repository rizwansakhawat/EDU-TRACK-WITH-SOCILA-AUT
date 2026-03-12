from django.shortcuts import render
from rest_framework import viewsets
from .serializers import InstituteSarializer
from .models import Institute
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsInstructor, IsSuperAdmin, IsStudent, IsOrgAdmin

# Create your views here.

class InstituteViewset(viewsets.ModelViewSet):
    serializer_class = InstituteSarializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        if user.role == "SUPERADMIN":
            return Institute.objects.all()
          
        return Institute.objects.filter(organization= user.organization)
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated , (IsSuperAdmin | IsOrgAdmin)]
        elif self.action in ["update", "partial_update"]:
            permission_classes =  [IsAuthenticated, IsOrgAdmin]
        elif self.action == "destroy":
            permission_classes = [IsAuthenticated, IsOrgAdmin]
        else:
            permission_classes = [IsAuthenticated]
    
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
        
    
    