import os
import time
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext
from main.models import User


def index(request):
    try:
        tmp = User.objects.get(sessionid=request.COOKIES.get('sessionid')).displayname
        return HttpResponse(render(request, "indexdeploy.html", {'BOTON': 'Deploy Pong', 'ACCION': 'run', 'username': tmp}))
    except:
        return HttpResponse(render(request, "indexdeploy.html", {'BOTON': 'Deploy Pong', 'ACCION': 'run'}))

def run(request):
    deploypass = os.environ["DEPLOY_PASSWORD"]
    if deploypass == "" or deploypass != request.POST.get("DEPLOY_PASSWORD"):
        return HttpResponseRedirect("/")
    else:
        os.popen("sudo mkdir /pong/basebackup")
        os.popen("sudo mkdir /pong/basenew")
        stream = os.popen("sudo git clone git@github.com:jesuserr/ft_transcendence.git /pong/basenew && sudo rm -r /pong/basebackup && sudo mv /pong/base /pong/basebackup && sudo mv /pong/basenew /pong/base")
        time.sleep(2)
        while os.path.exists("/pong/basenew"):
            time.sleep(1)
        #os.popen("pkill gunicorn")
        return HttpResponseRedirect("/")

def reboot(request):
    try:
        tmp = User.objects.get(sessionid=request.COOKIES.get('sessionid')).displayname
        return HttpResponse(render(request, "indexdeploy.html", {'BOTON': 'Reboot Pong', 'ACCION': 'rebootrun', 'username': tmp}))
    except:
        return HttpResponse(render(request, "indexdeploy.html", {'BOTON': 'Reboot Pong', 'ACCION': 'rebootrun'}))


def rebootrun(request):
    deploypass = os.environ["DEPLOY_PASSWORD"]
    if deploypass == "" or deploypass != request.POST.get("DEPLOY_PASSWORD"):
        return HttpResponseRedirect("/")
    os.popen("pkill gunicorn")
    return HttpResponseRedirect("/")
    