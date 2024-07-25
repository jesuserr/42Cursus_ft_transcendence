from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:tournament_name>/", views.tournament, name="tournament"),
]