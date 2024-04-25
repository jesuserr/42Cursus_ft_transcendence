from django.shortcuts import render
import hashlib
import time
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .forms import NewUserForm, LoginUserForm
from .models import User
from pong.utils import urlavatar

def index(request):
    try:
        tmp = User.objects.get(sessionid=request.COOKIES.get('sessionid'))
        response = render(request, 'indexmain.html', {'USERNAME': tmp.displayname, 'AVATAR': urlavatar(tmp.avatar)})
        return response
    except:
        return HttpResponseRedirect("login")
 
def newuser(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST, request.FILES)
        if form.is_valid():
            sessionid = hashlib.sha256(str(time.time()).encode('utf-8')).hexdigest()
            tmp = form.save(commit=False)
            tmp.password = hashlib.sha256(str(request.POST['password']).encode('utf-8')).hexdigest()
            tmp.sessionid = sessionid
            tmp.save()
            response = render(request, 'indexmain.html', {'USERNAME': tmp.displayname, 'AVATAR': urlavatar(tmp.avatar)})
            response.set_cookie('sessionid', sessionid)
            return response
        else:
            response = render(request, 'newuser.html', {'form': form, 'ACCION': 'Create User'})
            return response
    else:
        try:
            tmp = User.objects.get(sessionid=request.COOKIES.get('sessionid'))
            return HttpResponseRedirect("/")
        except:
             form = NewUserForm()
             response = render(request, 'newuser.html', {'form': form, 'ACCION': 'Create User'})
             return response

def edituser(request):
    #Falta el codigo de guardar los cambios
    try:
        tmp = User.objects.get(sessionid=request.COOKIES.get('sessionid'))
        form = NewUserForm(instance=tmp)
        form.initial["password"] = ""
        response = render(request, 'newuser.html', {'form': form, 'ACCION': 'Update User Data', 'USERNAME': tmp.displayname, 'AVATAR': urlavatar(tmp.avatar)})
        return response
    except:
        return HttpResponseRedirect("/")
    

def login(request):
    if request.method == 'POST':
        try:
            tmp = User.objects.get(email=request.POST['email'])
            if (tmp.password != hashlib.sha256(str(request.POST['password']).encode('utf-8')).hexdigest()):
                 form = LoginUserForm(request.POST)
                 response = render(request, 'login.html', {'form': form, 'ERROR': 'The password is wrong'})
                 return response
            else:
                sessionid = hashlib.sha256(str(time.time()).encode('utf-8')).hexdigest()
                tmp.sessionid = sessionid
                tmp.save()
                response = render(request, 'indexmain.html', {'USERNAME': tmp.displayname, 'AVATAR': urlavatar(tmp.avatar)})
                response.set_cookie('sessionid', sessionid)
                return response
        except:
            form = LoginUserForm(request.POST)
            response = render(request, 'login.html', {'form': form, 'ERROR': 'The user does not exist'})
            return response
    else:
        try:
            tmp = User.objects.get(sessionid=request.COOKIES.get('sessionid'))
            return HttpResponseRedirect("/")
        except:
            form = LoginUserForm()
            response = render(request, 'login.html', {'form': form})
            return response

def logoff(request):
    try:
        tmp = User.objects.get(sessionid=request.COOKIES.get('sessionid'))
        tmp.sessionid=""
        tmp.save()
        return HttpResponseRedirect("/")
    except:
        return HttpResponseRedirect("/")

