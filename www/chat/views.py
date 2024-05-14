from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect


def index(request):
    return HttpResponseRedirect("General")
    
def room(request, room_name):
    return render(request, "chat_main.html", {"room_name": room_name})
