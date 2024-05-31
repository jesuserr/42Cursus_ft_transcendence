from django.http import HttpResponse, HttpResponseRedirect
from .forms import NewUserForm, LoginUserForm, EditProfileUserForm, EditProfile42UserForm
from django.shortcuts import render
from django import forms
from django.core.mail import send_mail
import random
from .models import User, SecurityCode
import hashlib
import time
import os
from  .token import *

def tfa(request, tmpuser):
	if (request.POST.get('securitycode') == None):
		return tfasendcode(request, tmpuser)
	else:
		return tfacheckcode(request, tmpuser)

def tfacheckcode(request, tmpuser):
	try:
		tmp = SecurityCode.objects.get(email=request.POST['email'])
		if (tmp.code == request.POST['securitycode']):
			response = render(request, 'main_index.html', {'User': tmpuser})
			refresh = get_tokens_for_user(tmpuser)
			tokenid = str(refresh)
			tmpuser.tokenid = tokenid
			tmpuser.save()
			response.set_cookie('tokenid', tokenid)
			return response
		else:
			return tfasendcode(request, tmpuser, 'Invalid TFA security code, we have sent you a new one.')
	except:
		return tfasendcode(request, tmpuser, 'Invalid TFA security code, we have sent you a new one.')

def tfasendcode(request, tmpuser, error = ''):
	tmpcode = str(random.randint(100000,999999))
	FormData = {'Action': '', 'SecurityCode': 'input type=text name=securitycode maxlength=10 required="required"', 'TopMsg': '', 'ErrorMsg': ''}
	FormData['Action'] = 'Check Code'
	FormData['SecurityCode'] = 'input type=text name=securitycode maxlength=10 required="required"'
	FormData['ErrorMsg'] = error
	if (tmpuser.tfa_type == 1):
		# EMAIL
		FormData['TopMsg'] = 'We have sent you an email with a TFA security code, please enter it to verify TFA code.'
		try:
			send_mail("Pong42 TFA Security Code","Your Pong42 TFA security code is: " + tmpcode, "pong42pong@outlook.com",[tmpuser.email],fail_silently=False)
		except:
			FormData['ErrorMsg'] = 'Could not send the verification code, contact the administrator (probably the email account is blocked).'
	try:
		tmp = SecurityCode.objects.get(email=tmpuser.email)
		tmp.delete()
		tmp = SecurityCode()
		tmp.email = request.POST['email']
		tmp.code = tmpcode
		tmp.save() 
	except:
		tmp = SecurityCode()
		tmp.email = tmpuser.email
		tmp.code = tmpcode
		tmp.save()
	post_data = request.POST.copy()
	post_data['email'] = tmpuser.email
	form = LoginUserForm(post_data)
	form.fields['email'].widget = forms.HiddenInput()
	form.fields['password'].widget = forms.HiddenInput()
	form.errors['email'] = form.error_class()
	form.errors['password'] = form.error_class()
	response = render(request, 'main_tfa.html', {'form': form, 'Data': FormData})
	return response