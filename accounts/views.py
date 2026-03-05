from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .permissions import IsInstructor, IsOrgAdmin, IsStudent, IsSuperAdmin
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


from .models import User, Organization
from .serializers import UserSerializer, OrganizationsSerializer

# Create your views here.

class UserViewset(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['organization']
    search_fields = ['username', 'email']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == "SUPERADMIN":
            return User.objects.all()
        if user.role == "ORGADMIN":
            return User.objects.filter(organization=user.organization)
        return User.objects.filter(id=user.id)
    
    def get_permissions(self):
        
        if self.action == 'create':
            permission_classes = [IsAuthenticated , (IsOrgAdmin | IsSuperAdmin)]
        elif self.action in ["update", "partial_update"]:
            permission_classes =  [IsAuthenticated, IsOrgAdmin]
        elif self.action == "destroy":
            permission_classes = [IsAuthenticated, IsSuperAdmin]
        else:
            permission_classes = [IsAuthenticated]
    
        return [permission() for permission in permission_classes]
    
    
    # def perform_create(self, serializer):
    #     current_user = self.request.user
        
    #     target_role = self.request.data.get('role')
    #     if target_role == "SUPERADMIN" and current_user.role != "SUPERADMIN":
    #         raise ValidationError({"role":"You do not have permission to assign the SUPERADMIN role."})
            
    #     if current_user.role == "ORGADMIN":
    #         serializer.save(organization=current_user.organization)
    #     else:
    #         serializer.save()
        
        
        
    
        
        
    
    # #  Object-Level Protection --- define in serializer--******
    # def perform_update(self, serializer):
    #     instance = self.get_object()

    #     if (
    #         self.request.user.role == "ORGADMIN" and
    #         instance.organization != self.request.user.organization
    #     ):
    #         raise PermissionDenied("Cannot modify another organization user")

    #     serializer.save()

    # def perform_destroy(self, instance):
    #     if self.request.user.role != "SUPERADMIN":
    #         raise PermissionDenied("Only SuperAdmin can delete users")

    #     instance.delete()
    
     
        
    
class OrganizationViewset(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationsSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]
