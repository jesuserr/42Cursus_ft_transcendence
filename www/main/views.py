from django.http import HttpResponse, HttpResponseRedirect
from .userManagent import *
from django.core.mail import send_mail

def index(request):
    
	return 
def newuser(request):
	if not request.method == 'POST':
		#Request email
		return newUserEmailform(request)
	else:
		try:
			if request.POST['securitycode'] != '':
				#Check security code
				return newUserCheckCodeform(request)
			else:
				#Send and ask the security code
				return newUserSendCodeform(request)
		except:
			return HttpResponse("...")
    
	return HttpResponse("fianl")

def edituser(request):
    
	return
    

def login(request):
    
	return

def logoff(request):

	return 
def auth42(request):
    
	return

