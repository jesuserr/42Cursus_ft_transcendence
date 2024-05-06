from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

def index(request):
    return HttpResponseRedirect("GameTest")

def game(request, game_name):
    return render(request, "gamepong.html", {"game_name": game_name})