from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

def index(request):
    return HttpResponseRedirect("GameTest2")

def game2(request, game_name):
    return render(request, "gamepong2.html", {"game_name": game_name})