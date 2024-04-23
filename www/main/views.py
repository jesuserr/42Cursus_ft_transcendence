from django.shortcuts import render
import hashlib 
from django.http import HttpResponse
from django.template import loader
from .forms import UserForm
from .models import User


def index(request):
    print(request.COOKIES.get('sessionid'))
    if (str(request.COOKIES.get('sessionid')) == 'None'):
        template = loader.get_template("indexmain.html")
        return HttpResponse(template.render())
    else:
        
        return HttpResponse("tengo que revisar la cookie")

        
def newuser(request):
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = UserForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
             test = form.save(commit=False)
             test.password = hashlib.sha256(str(request.POST['password']).encode('utf-8')).hexdigest()
             test.sessionid = hashlib.sha256(str(request.POST['email']).encode('utf-8')).hexdigest() + hashlib.sha256(str(request.POST['password']).encode('utf-8')).hexdigest()
             test.save()
             return HttpResponse("Grabado")
        else:
            return HttpResponse(form.errors.as_data())
            
    else:
     email = 'cescanuela@gmail.com'
     #hashlib.sha256(email.encode('utf-8')).hexdigest()
     #if ()
     form = UserForm()
     response = render(request, 'newuser.html', {'form': form})
     response.set_cookie('sessionid', hashlib.sha256(email.encode('utf-8')).hexdigest())
     return response