from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from main.token import *

@token_required
def index(request):
    return HttpResponseRedirect("stats")