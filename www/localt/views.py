from django.shortcuts import render
from pongapi.token import *

@token_required
def index(request):
    return render(request, "localt_index.html")
