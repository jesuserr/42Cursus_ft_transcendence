from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
	path("welcome", views.welcome, name="welcome"),
    path("newuser", views.newuser, name="newuser"),
	path("edituser", views.edituser, name="edituser"),
	path("login", views.login, name="login"),
	path("logina", views.logina, name="logina"),
	path("logoff", views.logoff, name="logoff"),
	path("42auth", views.fourtytwo, name="fourtytwo"),
    path("game", views.game, name="game"),
    path("stats", views.stats, name="stats"),
	path("tournament", views.tournament, name="tournament"),

]
