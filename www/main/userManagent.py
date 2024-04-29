from django.http import HttpResponse, HttpResponseRedirect
from .forms import NewUserForm, LoginUserForm
from django.shortcuts import render
from django import forms
from django.core.mail import send_mail
import random
from .models import User, SecurityCode

FormData = {'Action': '', 'SecurityCode': 'input type=text name=securitycode maxlength=10 required="required"', 'TopMsg': '', 'ErrorMsg': ''}

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

def newUserCheckCodeform(request):
        FormData['Action'] = 'Check Code'
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

def NewUserCodeOkFillData(request):
        FormData['Action'] = 'Create User'
        FormData['SecurityCode'] = 'input type=hidden name=securitycode maxlength=10'
        FormData['TopMsg'] = request.POST['email']
        form = NewUserForm(request.POST)
        form.fields['email'].widget = forms.HiddenInput()
        response = render(request, 'newuser.html', {'form': form, 'Data': FormData})
        return response
        
        
               

