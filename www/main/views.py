from django.shortcuts import render
import hashlib 
from django.http import HttpResponse
from django.template import loader
from .forms import UserForm


def index(request):
    print(request.COOKIES.get('sessionid'))
    template = loader.get_template("indexmain.html")
    return HttpResponse(template.render())

def newuser(request):
    email = 'cescanuela@gmail.com'
    hashlib.sha256(email.encode('utf-8')).hexdigest()
    form = UserForm()
    response = render(request, 'newuser.html', {'form': form})
    response.set_cookie('sessionid', hashlib.sha256(email.encode('utf-8')).hexdigest())
    return response