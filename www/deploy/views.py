import os
import time
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


def index(request):
    template = loader.get_template("indexdeploy.html")
    return HttpResponse(template.render())

def run(request):
    os.popen("sudo mkdir /pong/basebackup")
    os.popen("sudo mkdir /pong/basenew")
    stream = os.popen("sudo git clone git@github.com:jesuserr/ft_transcendence.git /pong/basenew && sudo rm -r /pong/basebackup && sudo mv /pong/base /pong/basebackup && sudo mv /pong/basenew /pong/base")
    time.sleep(2)
    while os.path.exists("/pong/basenew"):
        time.sleep(1)
    os.popen("pkill gunicorn")
    return HttpResponse("Deploy finalizado")