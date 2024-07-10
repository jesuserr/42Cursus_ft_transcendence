from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from pongapi.token import *

@token_required
def index(request):
    return HttpResponseRedirect("General")
    
@token_required
def room(request, room_name):
    return render(request, "chat_main.html", {"room_name": room_name})
