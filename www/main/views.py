from django.http import HttpResponse, HttpResponseRedirect
from .userManagement import *
from .userManagement42 import *
from django.core.mail import send_mail
from .token import *

def welcome(request):
    response = render(request, "main_welcome.html")
    return response

def index(request):
	return maniPage(request)

def newuser(request):
	if not request.method == 'POST':
		#Request email
		return newUserEmailform(request)
	else:
		if request.POST.get('securitycode') != '':
			#Check security code
			return newUserCheckCodeform(request)
		elif (request.POST.get('securitycode') == ''):
			#Send and ask the security code
			return newUserSendCodeform(request)
	return HttpResponseRedirect("/")

@token_required
def edituser(request):
	return editProfile(request)
    
def login(request):
	return loginPage(request)
 
@token_required
def logoff(request):
	return logoffPage(request)

def fourtytwo(request):    
	return fourtytwoLogin(request)

def game(request):
    response = render(request, "main_game.html")
    return response
