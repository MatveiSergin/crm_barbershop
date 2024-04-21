from django.contrib.auth import login, get_user_model, logout
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from users.models import User
from users.serializers import UserSerializer
import datetime, jwt
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed("User not found")

        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password")

        payload = {
            "id": user.id,
            "exp": (datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp(),
            "iet": datetime.datetime.now().timestamp()
        }

        token = jwt.encode(payload=payload, key='secret', algorithm='HS256')

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