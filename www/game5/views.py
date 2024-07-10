from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from pongapi.token import *

@token_required
def index(request):
    return HttpResponseRedirect("game5Room")

@token_required
def game5(request, game_name):
    return render(request, "gamepong5.html", {"game_name": game_name})