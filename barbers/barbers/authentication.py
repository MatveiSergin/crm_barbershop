from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import jwt

class JWTAuthenticationFromPyJWT(BaseAuthentication):
    def authenticate(self, request):
        if request.path in ('/api/v1/users/login'):
            return None
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Invalid token')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('token is expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

        user = get_user_model().objects.get(id=payload['id'])

        return user, payload