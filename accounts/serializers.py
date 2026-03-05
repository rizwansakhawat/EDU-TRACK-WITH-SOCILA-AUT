from rest_framework import serializers
from .models import User, Organization
from rest_framework.exceptions import ValidationError

    
    
class OrganizationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"
        
        

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    organization = serializers.SlugRelatedField( slug_field='name',
    queryset=Organization.objects.all(),
     required=False, allow_null=True )
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'role', 'organization']
        
    def validate(self, data):
        # Access the user making the request
        request_user = self.context['request'].user
        target_role = data.get('role')
        target_org = data.get('organization')

        # 1. Role Protection: Only SUPERADMIN can create another SUPERADMIN
        if target_role == "SUPERADMIN" and request_user.role != "SUPERADMIN":
            raise ValidationError({"role": "Only SuperAdmins can assign the SuperAdmin role."})
        
        if request_user.role == "ORGADMIN":
            # Force the organization to be the same as the creator
            data['organization'] = request_user.organization
            
            # Prevent ORGADMIN from trying to pick another org
            if target_org and target_org != request_user.organization:
                raise ValidationError({"organization": "You cannot create users for other organizations."})

        return data


    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    