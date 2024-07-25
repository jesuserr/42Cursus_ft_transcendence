from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from pongapi.token import *

@token_required
def index(request):
    return HttpResponseRedirect("game6Room")

@token_required
def game6(request, game_name):
    return render(request, "gamepong6.html", {"game_name": game_name})