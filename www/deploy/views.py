import os
import subprocess
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


def index(request):
    template = loader.get_template("indexdeploy.html")
    return HttpResponse(template.render())

def run(request):
    stream = subprocess.run(["ls", "-l"], capture_output=True)
    return HttpResponse(stream.stdout)