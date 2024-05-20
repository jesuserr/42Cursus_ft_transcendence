from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

def index(request):
    return HttpResponseRedirect("GameTest3")

def game3(request, game_name):
    return render(request, "gamepong3.html", {"game_name": game_name})