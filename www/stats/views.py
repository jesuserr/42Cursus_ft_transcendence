from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from main.token import *

@token_required
def index(request):
    return HttpResponseRedirect("stats")

@token_required
def stats(request, stats_name):
    return render(request, "stats.html", {"stats_name": stats_name})