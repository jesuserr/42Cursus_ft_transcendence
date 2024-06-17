from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from main.token import *

@token_required
def index(request):
    return HttpResponseRedirect("All_star")
    
@token_required
def tournament(request, tournament_name):
    return render(request, "tournament_main.html", {"tournament_name": tournament_name})	