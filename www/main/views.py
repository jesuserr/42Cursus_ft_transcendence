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
		try:
			if request.POST['securitycode'] != '':
				#Check security code
				return newUserCheckCodeform(request)
			elif (request.POST['securitycode'] == ''):
				#Send and ask the security code
				return newUserSendCodeform(request)
		except:
			pass
	return HttpResponseRedirect("/")

def edituser(request):
    
	return HttpResponse('edituser')
    
def login(request):
    
	return HttpResponse('login')
 
def logoff(request):

	return HttpResponse('logoff')

def auth42(request):
    
	return HttpResponse('42auth')
