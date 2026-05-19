from rest_framework import authentication, exceptions
from django.conf import settings
from django.utils import timezone
import jwt
from .models import User, UserSession

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get('user_id')
            
            # Check if session is valid
            try:
                session = UserSession.objects.get(token=token, user_id=user_id, is_active=True)
                if session.expires_at < timezone.now():
                    session.is_active = False
                    session.save()
                    raise exceptions.AuthenticationFailed('Token has expired')
            except UserSession.DoesNotExist:
                raise exceptions.AuthenticationFailed('Invalid token')
            
            user = User.objects.get(id=user_id)
            return (user, token)
            
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')