from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
	path("run", views.run, name="run"),
	path("reboot", views.reboot, name="reboot"),
	path("rebootrun", views.rebootrun, name="rebootrun"),
]