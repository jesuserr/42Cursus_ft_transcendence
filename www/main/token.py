from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.http import HttpResponseRedirect


def get_user_from_token(token):
    decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    user_id = decoded_token['user_id']
    User = get_user_model()
    user = User.objects.get(id=user_id)
    return user

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)
    
class OneMinuteToken(RefreshToken):
    lifetime = timedelta(minutes=1)

def get_one_minute_tokens_for_user(user):
    refresh = OneMinuteToken.for_user(user)
    return str(refresh.access_token)


def token_required(f):
    def decorator(request, *args, **kwargs):
        try:
            token = request.COOKIES.get('tokenid')
            tmpuser = get_user_from_token(token)
        except:
            return HttpResponseRedirect("/")
        return f(request, *args, **kwargs)
    return decorator