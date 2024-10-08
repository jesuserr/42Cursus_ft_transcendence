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
from twilio.rest import Client
import pyotp
import qrcode

def send_sms(phone_number, message):
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=message,
        from_= os.environ.get('TWILIO_PHONE_NUMBER'),
        to=phone_number
    )

def tfa(request, tmpuser):
	if (request.POST.get('securitycode') == None):
		return tfasendcode(request, tmpuser)
	else:
		return tfacheckcode(request, tmpuser)

def tfacheckcode(request, tmpuser):
	try:
		tmpusertoken = get_user_from_token(request.COOKIES['tokenid'], os.environ.get('DJANGO_SECRET_KEY_TFA'))
		tmp = SecurityCode.objects.get(email=tmpusertoken.email)
		if (tmpuser.tfa_type == 3):
			totp = pyotp.TOTP(tmpuser.totp_secret)
			if totp.verify(request.POST['securitycode']):
				tmp.code = request.POST['securitycode']
		if (tmp.code == request.POST['securitycode']):
			response = render(request, 'main_root.html', {'User': tmpuser})
			refresh = get_tokens_for_user(tmpuser)
			tokenid = str(refresh)
			tmpuser.tokenid = tokenid
			tmpuser.save()
			response.set_cookie('tokenid', tokenid, secure=True, httponly=True)
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
		FormData['TopMsg'] = 'We have sent you an email with a TFA security code, please enter it to verify TFA code. (valid for 5 minutes)'
		try:
			send_mail("Pong42 TFA Security Code","Your Pong42 TFA security code is: " + tmpcode, "pong42pong@outlook.com",[tmpuser.email],fail_silently=False)
		except:
			FormData['ErrorMsg'] = 'Could not send the verification code, contact the administrator (probably the email account is blocked).'
	elif (tmpuser.tfa_type == 2):
		# SMS
		FormData['TopMsg'] = 'We have sent you an SMS with a TFA security code, please enter it to verify TFA code. (valid for 5 minutes)'
		try:
			send_sms(tmpuser.phone_number, "Your Pong42 TFA security code is: " + tmpcode)
		except:
			FormData['ErrorMsg'] = 'Could not send the verification code, check is phone number is the right format or contact the administrator (probably the twilio access data is invalid).'
	elif (tmpuser.tfa_type == 3):
		# Google Authenticator
		FormData['TopMsg'] = 'Please enter the TFA security code from your Google Authenticator app. (valid for 30 seconds)'
		try:
			totp = pyotp.TOTP(tmpuser.totp_secret)
			totp_url = totp.provisioning_uri(name=tmpuser.email, issuer_name='Pong42')
			qr = qrcode.make(totp_url)
			qr = qr.resize((300, 300))
			qr_filename = f'static/qr_codes/qr_code_{tmpuser.id}.png'
			qr.save(qr_filename)
			FormData['QRCode'] = qr_filename
		except:
			FormData['ErrorMsg'] = 'Could not generate the QR code, contact the administrator.'
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
	refresh = get_five_minute_tokens_for_user(tmpuser, os.environ.get('DJANGO_SECRET_KEY_TFA'))
	tokenid = str(refresh)                          
	response.set_cookie('tokenid', tokenid, secure=True, httponly=True)
	return response