from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
	path("newuser", views.newuser, name="newuser"),
	path("edituser", views.edituser, name="edituser"),
	path("login", views.login, name="login"),
	path("logoff", views.logoff, name="logoff"),
	path("42auth", views.fourtytwo, name="fourtytwo"),
]