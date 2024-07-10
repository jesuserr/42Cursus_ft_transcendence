from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:game_name>/", views.game6, name="game6"),
]