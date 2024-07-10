from django.shortcuts import render

def index(request):
    return render(request, "localt_index.html")
