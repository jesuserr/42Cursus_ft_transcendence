from django.http import HttpResponse, HttpResponseRedirect
from .userManagement import *
from .userManagement42 import *
from django.core.mail import send_mail
from .token import *

@token_required
def spa(request):
	response = render(request, "main_spa.html")
	return response

def welcome(request):
	FormDataLogin = {'ErrorMsg': '', 'URL42': os.environ["URL42"]}
	response = render(request, 'main_welcome.html', {'Data': FormDataLogin})
	return response

def index(request):
	response = render(request, "main_spa.html")
	return response

def main(request):
	return mainPage(request)

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

def logina(request):
	return AnonimousUser(request)
 
@token_required
def logoff(request):
	return logoffPage(request)

def fourtytwo(request):    
	return fourtytwoLogin(request)

def logini(request):
	response = render(request, "main_logini.html")
	return response

@token_required
def edituseri(request):
	token = request.COOKIES.get('tokenid')
	tmp = get_user_from_token(token)
	response = render(request, "main_edituseri.html", {'User': tmp})
	return response

@token_required
def game2(request):
	token = request.COOKIES.get('tokenid')
	tmp = get_user_from_token(token)
	response = render(request, "main_game2.html", {'User': tmp})
	return response

@token_required
def game3(request):
	token = request.COOKIES.get('tokenid')
	tmp = get_user_from_token(token)
	response = render(request, "main_game3.html", {'User': tmp})
	return response

@token_required
def game4(request):
	token = request.COOKIES.get('tokenid')
	tmp = get_user_from_token(token)
	response = render(request, "main_game4.html", {'User': tmp})
	return response

@token_required
def stats(request):
	token = request.COOKIES.get('tokenid')
	tmp = get_user_from_token(token)
	response = render(request, "main_stats.html", {'User': tmp})
	return response

@token_required
def tournament(request):
	token = request.COOKIES.get('tokenid')
	tmp = get_user_from_token(token)
	response = render(request, "main_tournament.html", {'User': tmp})
	return response

@token_required
def localt(request):
	token = request.COOKIES.get('tokenid')
	tmp = get_user_from_token(token)
	response = render(request, "main_localt.html", {'User': tmp})
	return response