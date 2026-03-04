from rest_framework import serializers
from .models import User, Organization
    
    
class OrganizationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"
        
        

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    organization = serializers.SlugRelatedField( slug_field='name', queryset=Organization.objects.all())
    

    class Meta:
        model = User
        fields = ['username', 'password', 'role', 'organization']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
        
        