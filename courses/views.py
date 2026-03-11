from django.shortcuts import render
from .models import Course
from .serializers import CoureSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

# Create your views here.


class CouserViewset(viewsets.ModelViewSet):
    serializer_class = CoureSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        if user.role == "SUPERADMIN":
            return Course.objects.all()
        return Course.objects.filter(institute__organization=user.organization)
    
    def perform_create(self, serializer):
        serializer.save(instructor= self.request.user)
    
    
    
    
