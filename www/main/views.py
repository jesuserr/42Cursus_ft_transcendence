from django.http import HttpResponse, HttpResponseRedirect
from .userManagent import *
from django.core.mail import send_mail

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

def edituser(request):
	return HttpResponse('edituser')
    
def login(request):
	return loginPage(request)
 
def logoff(request):
	return logoffPage(request)

def fourtwo(request):
    
	return HttpResponse('42auth')
