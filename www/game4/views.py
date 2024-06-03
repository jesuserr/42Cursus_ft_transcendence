from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from main.token import *

@token_required
def index(request):
    return HttpResponseRedirect("game4Room")

@token_required
def game4(request, game_name):
    return render(request, "gamepong4.html", {"game_name": game_name})