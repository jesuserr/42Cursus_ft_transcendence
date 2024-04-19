import os
import subprocess
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


def index(request):
    template = loader.get_template("indexdeploy.html")
    return HttpResponse(template.render())

def run(request):
    stream = os.popen("git fetch && git reset --hard HEAD && git merge origin/$CURRENT_BRANCH")
    return HttpResponse(stream.read)