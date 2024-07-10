from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from pongapi.token import *

@token_required
def index(request):
    return render(request, "friends_pongapi.html")