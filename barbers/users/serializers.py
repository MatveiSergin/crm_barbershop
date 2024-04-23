from django.contrib.auth import get_user_model
from rest_framework import serializers

from corp.serializers import StaffSerializer
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    staff = StaffSerializer()
    class Meta:
        model = get_user_model()
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'staff', 'username')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        staff_data = validated_data.pop('staff')
        staff_serializer = StaffSerializer(data=staff_data)
        staff_serializer.is_valid(raise_exception=True)
        staff = staff_serializer.save()
        #password = validated_data.pop('password', None)
        #instance = self.Meta.model(**validated_data)
        #staff_data = validated_data.pop('staff')
        #if password is not None:
        #    instance.set_password(password) #hashed password
        #instance.save()

        #return instance