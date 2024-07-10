from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
	path("main", views.main, name="main"),
	path("welcome", views.welcome, name="welcome"),
    path("newuser", views.newuser, name="newuser"),
	path("edituser", views.edituser, name="edituser"),
	path("login", views.login, name="login"),
	path("logina", views.logina, name="logina"),
	path("logoff", views.logoff, name="logoff"),
	path("42auth", views.fourtytwo, name="fourtytwo"),
	path("game2", views.game2, name="game2"),
    path("game3", views.game3, name="game3"),
	path("game4", views.game4, name="game4"),
	path("logini", views.logini, name="logini"),
	path("edituseri", views.edituseri, name="edituseri"),
    path("stats", views.stats, name="stats"),
	path("tournament", views.tournament, name="tournament"),
	path("spa", views.spa, name="spa"),

]
