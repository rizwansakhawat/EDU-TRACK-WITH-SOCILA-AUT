from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .permissions import IsInstructor, IsOrgAdmin, IsStudent, IsSuperAdmin
from rest_framework.exceptions import PermissionDenied

from .models import User, Organization
from .serializers import UserSerializer, OrganizationsSerializer

# Create your views here.

class UserViewset(viewsets.ModelViewSet):
    # queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == "SUPERADMIN":
            return User.objects.all()
        
        if user.role == "ORGADMIN":
            return User.objects.filter
        
        return User.objects.filter(id=User.id)
    
    def get_permissions(self):
        
        if self.action == 'create':
            return [IsAuthenticated(), IsOrgAdmin()]
        if self.action in ["update", "partial_update"]:
            return [IsAuthenticated(), IsOrgAdmin()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsSuperAdmin()]
        
        return [IsAuthenticated()]
    
     
        
    
class OrganizationViewset(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationsSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]
