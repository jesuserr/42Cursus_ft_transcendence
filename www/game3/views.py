from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from main.token import *

@token_required
def index(request):
    return HttpResponseRedirect("game3Room")

@token_required
def game3(request, game_name):
    return render(request, "gamepong3.html", {"game_name": game_name})