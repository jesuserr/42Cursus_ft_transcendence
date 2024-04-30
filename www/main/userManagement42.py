from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django import forms
from .models import User
import requests


def fourtytwoLogin(request):
	accesscode = request.GET.get('code')
	url = 'https://api.intra.42.fr/oauth/token'
	postdata = {
        'grant_type': 'authorization_code',
        'client_id' : 'u-s4t2ud-38baf166fb3ab0e52361312910fa3d2e092d59ac233a0b66c4410ba09eed6cc8',
		'client_secret' : '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',
		'code' : accesscode,
		'redirect_uri': 'https://localhost/main/42auth',
    }
	r = requests.post(url, data=postdata)
	t = r.json()
	r1=requests.get("https://api.intra.42.fr/v2/me", headers={"Authorization": "Bearer " + t['access_token']})
	r2 = r1.json()
	print(r2)
	return HttpResponse(r2['email'])