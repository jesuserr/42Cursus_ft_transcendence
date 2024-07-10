from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from pongapi.token import *

@token_required
def index(request):
    return HttpResponseRedirect("gameRoom")

@token_required
def game(request, game_name):
    return render(request, "gamepong.html", {"game_name": game_name})