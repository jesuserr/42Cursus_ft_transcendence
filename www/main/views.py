from django.shortcuts import render
import hashlib 
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
            tmp = form.save(commit=False)
            tmp.password = hashlib.sha256(str(request.POST['password']).encode('utf-8')).hexdigest()
            tmp.sessionid = hashlib.sha256(str(request.POST['email']).encode('utf-8')).hexdigest()
            tmp.save()
            response = render(request, 'indexmain.html', {'username': tmp.email})
            response.set_cookie('sessionid', hashlib.sha256(str(request.POST['email']).encode('utf-8')).hexdigest())
            return response
        else:
            response = render(request, 'newuser.html', {'form': form})
            return response
            
    else:
        form = NewUserForm()
        response = render(request, 'newuser.html', {'form': form})
        return response
    

def edituser(request):
    return HttpResponse('EDITUSER')

def login(request):
    form = LoginUserForm()
    response = render(request, 'login.html', {'form': form})
    return response
    

def logoff(request):
    return HttpResponse('logoff')

