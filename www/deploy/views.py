import os
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


def index(request):
    template = loader.get_template("indexdeploy.html")
    return HttpResponse(template.render())

def run(request):
    stream = os.popen('ls -la')
    output = stream.read()
    return HttpResponse(output)