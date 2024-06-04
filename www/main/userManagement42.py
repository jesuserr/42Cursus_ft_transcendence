from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django import forms
from .models import User
import requests
import os
import hashlib
import time
from  .token import *
from .userManagementTFA import *
import pyotp

## Fourty Two Login 

FormData = {'ErrorMsg': ''}

def fourtytwoLogin(request):
	#if tfa is enabled and need to check the security code
	if request.method == 'POST':
		return tfa(request, User.objects.get(email=request.POST['email']))
	try:
		## Get information for 42 network
		accesscode = request.GET.get('code')
		url = 'https://api.intra.42.fr/oauth/token'
		postdata = {
			'grant_type': 'authorization_code',
			'client_id' : os.environ["CLIENT_ID"],
			'client_secret' : os.environ["CLIENT_SECRET"],'code' : accesscode,
			'redirect_uri': os.environ["REDIRECT_URI"],
			}
		requestToken = requests.post(url, data=postdata)
		requestUserProfile=requests.get("https://api.intra.42.fr/v2/me", headers={"Authorization": "Bearer " + requestToken.json()['access_token']})
		UserProfile42 = requestUserProfile.json()
		try:
			## check if the user exist in teh database
			tmpuser =  User.objects.get(email=UserProfile42['email'])
			## if the user exist however is not from 42 network
			if (tmpuser.fourtytwo == False):
				FormData['ErrorMsg'] = 'This email is already registered in the database but not through 42 network.'
				response = render(request, 'main_showmsg.html', {'Data': FormData})
				return response
		except:
			## if a new user
			tmpuser = User()
			tmpuser.totp_secret = pyotp.random_base32()
		##common code for new and already in the database	
		refresh = RefreshToken.for_user(tmpuser)
		tokenid = str(refresh.access_token)
		tmpuser.password = hashlib.sha256(str(datetime.now(timezone.utc)).encode('utf-8')).hexdigest()
		tmpuser.email = UserProfile42['email']
		tmpuser.displayname = UserProfile42['displayname']
		tmpuser.avatar = UserProfile42['image']['link']
		tmpuser.tokenid = tokenid
		tmpuser.fourtytwo = True
		tmpuser.save()
		refresh = RefreshToken.for_user(tmpuser)
		tokenid = str(refresh.access_token)
		tmpuser.tokenid = tokenid
		tmpuser.save()
		if (tmpuser.tfa == True):
			return tfa(request, tmpuser)
		FormData['ErrorMsg'] = 'You have logged in with the user of 42'
		response = render(request, 'main_index.html', {'Data': FormData, 'User': tmpuser})
		response.set_cookie('tokenid', tokenid, secure=True, httponly=True)
		return response
	except:
		FormData['ErrorMsg'] = 'Something was not working as expected, contact the administrator (probably the connectivity data to 42 is not correct).'
		response = render(request, 'main_showmsg.html', {'Data': FormData})
		return response
		