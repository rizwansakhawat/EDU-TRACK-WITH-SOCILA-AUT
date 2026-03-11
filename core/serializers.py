from rest_framework import serializers
from .models import Institute


class InstituteSarializer(serializers.ModelSerializer):
    class Meta:
        model = Institute
        fields = "__all__"
        read_only_fields = ['organization']
        
    