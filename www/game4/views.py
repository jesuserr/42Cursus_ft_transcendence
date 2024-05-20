from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

def index(request):
    return HttpResponseRedirect("GameTest4")

def game4(request, game_name):
    return render(request, "gamepong4.html", {"game_name": game_name})