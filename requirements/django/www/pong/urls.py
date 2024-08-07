"""
URL configuration for pong project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
	path("", views.index, name="index"),
	path("pongapi/", include("pongapi.urls")),
	path("deploy/", include("deploy.urls")),
	path("chat/", include("chat.urls")),
	path("game/", include("game.urls")),
	path("game2/", include("game2.urls")),
    path("game3/", include("game3.urls")),
    path("game4/", include("game4.urls")),
    path("game5/", include("game5.urls")),
    path("game6/", include("game6.urls")),
	path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("stats/", include("stats.urls")),
	path("friends/", include("friends.urls")),
	path("tournament/", include("tournament.urls")),
	path("localt/", include("localt.urls")),
]
