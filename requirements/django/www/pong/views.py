from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

def index(request):
	response = render(request, "main_spa.html")
	return response

