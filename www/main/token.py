from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model


def get_user_from_token(token):
    decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    user_id = decoded_token['user_id']
    User = get_user_model()
    user = User.objects.get(id=user_id)
    return user

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)
    
