from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers

from corp.models import Staff
from corp.serializers import StaffSerializer, BarbershopSerializer
from users.models import User

class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    surname = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=120)
    staff_id = serializers.IntegerField()
    def create(self, validated_data):
        return get_user_model().objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['name'],
            last_name=validated_data['surname'],
            staff=Staff.objects.get(id=validated_data['staff_id'])
        )

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email', None)

        if email is None:
            return serializers.ValidationError('Please provide an email address')

        password = data.get('password', None)

        if password is None:
            return serializers.ValidationError('Please provide a password')

        user = authenticate(username=email, password=password)

        if user is None:
            return serializers.ValidationError('Invalid email or password')

        if not user.is_active:
            return serializers.ValidationError('This user has been deactivated')

        return {
            "email": email,
            "password": password
        }