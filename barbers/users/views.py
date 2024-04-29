from django.contrib.auth import login, get_user_model, logout, authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import Group
from corp.serializers import StaffSerializer
from users.serializers import LoginSerializer, RegisterSerializer


class RegisterView(APIView):
    def post(self, request):
        password = request.data.pop('password')
        staff_serializer = StaffSerializer(data=request.data)
        staff_serializer.is_valid(raise_exception=True)
        staff = staff_serializer.save()

        user_serializer = RegisterSerializer(data={
            'name': staff.name,
            'surname': staff.surname,
            'email': staff.mail,
            'password': password,
            'staff_id': staff.pk
        })
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        user.add_group_by_position()

        return Response({
            'login': user.username,
            'password': password
        },
            status=status.HTTP_201_CREATED)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email, password = serializer.data['email'], serializer.data['password']
        user = authenticate(username=email, password=password)
        token = user.get_token()
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }

        login(request, user)
        return response


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie(key='jwt')
        response.data = {
            'message': 'success'
        }
        logout(request)
        return response