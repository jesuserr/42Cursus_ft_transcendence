from django.shortcuts import render
import hashlib
import time
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .forms import NewUserForm, LoginUserForm
from .models import User


def index(request):
    try:
        tmp = User.objects.get(sessionid=request.COOKIES.get('sessionid')).displayname
        response = render(request, 'indexmain.html', {'username': tmp})
        return response
    except:
        return HttpResponseRedirect("login")
 
def newuser(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            sessionid = hashlib.sha256(str(time.time()).encode('utf-8')).hexdigest()
            tmp = form.save(commit=False)
            tmp.password = hashlib.sha256(str(request.POST['password']).encode('utf-8')).hexdigest()
            tmp.sessionid = sessionid
            tmp.save()
            response = render(request, 'indexmain.html', {'username': tmp.displayname})
            response.set_cookie('sessionid', sessionid)
            return response
        else:
            response = render(request, 'newuser.html', {'form': form})
            return response
            
    else:
        try:
            tmp = User.objects.get(sessionid=request.COOKIES.get('sessionid')).displayname
            response = render(request, 'indexmain.html', {'username': tmp})
            return response
        except:
             form = NewUserForm()
             response = render(request, 'newuser.html', {'form': form})
             return response
    

def edituser(request):
    return HttpResponse('EDITUSER')

def login(request):
    try:
        tmp = User.objects.get(sessionid=request.COOKIES.get('sessionid')).displayname
        response = render(request, 'indexmain.html', {'username': tmp})
        return response
    except:
        form = LoginUserForm()
        response = render(request, 'login.html', {'form': form})
        return response
    

def logoff(request):
    return HttpResponse('logoff')

