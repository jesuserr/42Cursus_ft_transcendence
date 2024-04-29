from django.http import HttpResponse, HttpResponseRedirect
from .forms import NewUserForm, LoginUserForm
from django.shortcuts import render
from django import forms
from django.core.mail import send_mail
import random
from .models import User, SecurityCode
import hashlib
import time

## Main page ##

def maniPage(request):
    try:
        print(sessionid=request.COOKIES.get('sessionid'))
        tmp = User.objects.get(sessionid=request.COOKIES.get('sessionid'))
        response = render(request, 'indexmain.html', {'USERNAME': 'tmp.displayname', 'AVATAR': 'urlavatar(tmp.avatar)'})
        return response
    except:
        return HttpResponseRedirect("login")
        
## New user section ##

#Dictionary for the new user form
FormData = {'Action': '', 'SecurityCode': 'input type=text name=securitycode maxlength=10 required="required"', 'TopMsg': '', 'ErrorMsg': ''}
#New user form asking for your email address
def newUserEmailform(request, error = ''):
        FormData['Action'] = 'Check Email'
        FormData['SecurityCode'] = 'input type=hidden name=securitycode maxlength=10'
        FormData['TopMsg'] = 'Specify with which email address you want to register.'
        FormData['ErrorMsg'] = error
        form = NewUserForm()
        form.fields['password'].widget = forms.HiddenInput()
        form.fields['displayname'].widget = forms.HiddenInput()
        form.fields['avatar'].widget = forms.HiddenInput()
        response = render(request, 'newuser.html', {'form': form, 'Data': FormData})
        return response

#New user form that sends you the security code and checks it.
def newUserSendCodeform(request, error = ''):
        try:
                tmp = User.objects.get(email=request.POST['email'])
                return newUserEmailform(request, error = 'The indicated email already exists.')
        except:
               pass
        FormData['Action'] = 'Check Code'
        FormData['SecurityCode'] = 'input type=text name=securitycode maxlength=10 required="required"'
        FormData['TopMsg'] = 'We have sent you an email with a security code, please enter it to verify your email address.'
        FormData['ErrorMsg'] = error
        tmpcode = str(random.randint(100000,999999))
        try:
               send_mail("Pong42 Security Code","Your Pong42 security code is: " + tmpcode, "pong42pong@outlook.com",[request.POST['email']],fail_silently=False)
        except:
               FormData['ErrorMsg'] = 'Could not send the verification code, contact the administrator (probably the email account is blocked).'
        try:
                tmp = SecurityCode.objects.get(email=request.POST['email'])
                tmp.delete()
                tmp = SecurityCode()
                tmp.email = request.POST['email']
                tmp.code = tmpcode
                tmp.save() 
        except:
                tmp = SecurityCode()
                tmp.email = request.POST['email']
                tmp.code = tmpcode
                tmp.save()
        form = NewUserForm(request.POST)
        form.fields['email'].widget = forms.HiddenInput()
        form.fields['password'].widget = forms.HiddenInput()
        form.fields['displayname'].widget = forms.HiddenInput()
        form.fields['avatar'].widget = forms.HiddenInput()
        form.errors['password'] = form.error_class()
        form.errors['displayname'] = form.error_class()
        response = render(request, 'newuser.html', {'form': form, 'Data': FormData})
        return response

##Function that checks the security code
def newUserCheckCodeform(request):
        FormData['Action'] = 'Check Code'
        if (request.POST['securitycode'] == ''):
                FormData['SecurityCode'] = 'input type=text name=securitycode maxlength=10 required="required"'
        FormData['TopMsg'] = 'We have sent you an email with a security code, please enter it to verify your email address.'
        try:
               tmp = SecurityCode.objects.get(email=request.POST['email'])
               if (tmp.code == request.POST['securitycode']):
                       return NewUserCodeOkFillData(request)
               else:
                       return newUserSendCodeform(request, 'The security code entered is not valid, we have sent you a new one, please try again. ')
        except:
                return newUserSendCodeform(request, 'This email does not have any pending security code.....')

#Function that once the security code has been confirmed asks for the other data.
def NewUserCodeOkFillData(request):
        form = NewUserForm(request.POST, request.FILES)
        try:
                tmp = SecurityCode.objects.get(email=request.POST['email'])
                if (request.POST['password'] != "" and tmp.code == request.POST['securitycode'] and form.is_valid()):
                        sessionid = hashlib.sha256(str(time.time()).encode('utf-8')).hexdigest()
                        formtmp = form.save(commit=False)
                        formtmp.password = hashlib.sha256(str(request.POST['password']).encode('utf-8')).hexdigest()
                        formtmp.sessionid = sessionid
                        formtmp.save()
                        ##revisar desde
                        response = render(request, 'indexmain.html', {'USERNAME': 'tmp.displayname', 'AVATAR': 'urlavatar(tmp.avatar)'})
                        response.set_cookie('sessionid', sessionid)
                        print("grabar session + " + sessionid)
                        return response
                		##hasta aqui
        except:
                return HttpResponseRedirect("/")      
        FormData['Action'] = 'Create User'
        FormData['SecurityCode'] = 'input type=hidden name=securitycode maxlength=10 value=' + request.POST['securitycode']
        FormData['TopMsg'] = request.POST['email']
        form.fields['email'].widget = forms.HiddenInput()
        response = render(request, 'newuser.html', {'form': form, 'Data': FormData})
        return response
        