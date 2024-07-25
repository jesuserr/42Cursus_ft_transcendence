from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
	path("friend", views.friend, name="friend"),
	path("friendstat", views.friendstat, name="friendstat"),
]