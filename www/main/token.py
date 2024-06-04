from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from datetime import *
from django.http import HttpResponseRedirect
from jwt.exceptions import ExpiredSignatureError
import os


def get_user_from_token(token, secret_key = settings.SECRET_KEY):
    decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
    user_id = decoded_token['user_id']
    User = get_user_model()
    user = User.objects.get(id=user_id)
    return user

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)
    
class FiveMinuteToken(RefreshToken):
    lifetime = timedelta(seconds=300)

def get_five_minute_tokens_for_user(user, secret_key = settings.SECRET_KEY):
    refresh = FiveMinuteToken.for_user(user)
    token = {
        'token_type': 'access', 
        'exp': datetime.now(timezone.utc) + timedelta(seconds=300),  
        'jti': refresh.access_token.payload['jti'], 
        'user_id': user.id
    }
    encoded_jwt = jwt.encode(token, secret_key, algorithm='HS256')
    return encoded_jwt


def token_required(f):
    def decorator(request, *args, **kwargs):
        try:
            token = request.COOKIES.get('tokenid')
            jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"]) 
            tmpuser = get_user_from_token(token)
        except ExpiredSignatureError:
            return HttpResponseRedirect("/")
        except:
            return HttpResponseRedirect("/")
        return f(request, *args, **kwargs)
    return decorator