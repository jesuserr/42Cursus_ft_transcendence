from django.shortcuts import render
import hashlib
import time
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .forms import NewUserForm, LoginUserForm
from .models import User, SecurityCode
from pong.utils import urlavatar
from django import forms
from django.core.mail import send_mail
import random

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
        if not (form.is_valid()):
            form.fields['avatar'].widget = forms.HiddenInput()
            return render(request, 'newuser.html', {'form': form, 'ACCION': 'Create User', 'SECURITYCODE': 'input type=hidden name=securitycode maxlength=10'})
        elif not (str(request.POST['securitycode'])):
            tmpcode = str(random.randint(100000,999999))
            form = NewUserForm(request.POST, request.FILES)
            send_mail("Pong42 Security Code","Your Pong42 security code is: " + tmpcode,"pong42pong@outlook.com",[request.POST['email']],fail_silently=False)
            form.fields['email'].widget = forms.HiddenInput()
            form.fields['password'].widget = forms.HiddenInput()
            form.fields['displayname'].widget = forms.HiddenInput()
            form.fields['avatar'].widget = forms.HiddenInput()
            response = render(request, 'newuser.html', {'form': form, 'ACCION': 'Security Code', 'SECURITYCODE': 'input type=text name=securitycode maxlength=10'})
            try:
                 tmp = SecurityCode.objects.get(email=request.POST['email'])
                 tmp.delete()
                 tmp = SecurityCode()
                 tmp.email = request.POST['email']
                 tmp.code = tmpcode
                 tmp.save() 
            except:
                tmp = SecurityCode()
                tmp.email = request.POST['email']
                tmp.code = tmpcode
                tmp.save() 
            return response
        else:
            form = NewUserForm(request.POST, request.FILES)
            print(SecurityCode.objects.get(email=request.POST['email']).code)
            print(request.POST['securitycode'])
            if form.is_valid() and SecurityCode.objects.get(email=request.POST['email']).code == request.POST['securitycode']:
                sessionid = hashlib.sha256(str(time.time()).encode('utf-8')).hexdigest()
                tmp = form.save(commit=False)
                tmp.password = hashlib.sha256(str(request.POST['password']).encode('utf-8')).hexdigest()
                tmp.sessionid = sessionid
                tmp.save()
                response = render(request, 'indexmain.html', {'USERNAME': tmp.displayname, 'AVATAR': urlavatar(tmp.avatar)})
                response.set_cookie('sessionid', sessionid)
                return response
            else:
                form = NewUserForm(request.POST, request.FILES)
                form.fields['email'].widget = forms.HiddenInput()
                form.fields['password'].widget = forms.HiddenInput()
                form.fields['displayname'].widget = forms.HiddenInput()
                form.fields['avatar'].widget = forms.HiddenInput()
                response = render(request, 'newuser.html', {'form': form, 'ACCION': 'Security Code', 'SECURITYCODE': 'input type=text name=securitycode maxlength=10'})
                return response
    else:
        try:
            tmp = User.objects.get(sessionid=request.COOKIES.get('sessionid'))
            return HttpResponseRedirect("/")
        except:
             form = NewUserForm()
             form.fields['avatar'].widget = forms.HiddenInput()
             response = render(request, 'newuser.html', {'form': form, 'ACCION': 'Create User', 'SECURITYCODE': 'input type=hidden name=securitycode maxlength=10'})
             return response

def edituser(request):
    if request.method == 'POST':
        try:
             tmp = User.objects.get(sessionid=request.COOKIES.get('sessionid'))
             form = NewUserForm(request.POST, request.FILES, instance=tmp)
             if form.is_valid():
                tmp = form.save(commit=False)
                tmp.password = hashlib.sha256(str(request.POST['password']).encode('utf-8')).hexdigest()
                tmp.save()
                return HttpResponseRedirect("/")
        except:
            return HttpResponseRedirect("/")
    try:
        tmp = User.objects.get(sessionid=request.COOKIES.get('sessionid'))
        form = NewUserForm(instance=tmp)
        form.initial["password"] = ""
        form.fields['email'].widget = forms.HiddenInput()
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

