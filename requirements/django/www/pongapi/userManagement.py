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
from .userManagementTFA import *
import pyotp
import random
import string


## EditProfile ##

def editProfile(request):
    FormData = {'Action': 'Save Changes', 'SecurityCode': '/"', 'TopMsg': '', 'ErrorMsg': ''}
    try:
        token = request.COOKIES.get('tokenid')
        tmpuser = get_user_from_token(token)
    except:
        return HttpResponseRedirect("/")
    if not request.method == 'POST':
            if (tmpuser.fourtytwo == False):
                form = EditProfileUserForm(instance=tmpuser)
                form.fields['email'].widget.attrs['readonly'] = True
                form.initial["password"] = ''
                response = render(request, 'main_newuser.html', {'form': form, 'User': tmpuser, 'Data': FormData})
                return response
            else:
                form = EditProfile42UserForm(instance=tmpuser)
                response = render(request, 'main_newuser.html', {'form': form, 'User': tmpuser, 'Data': FormData})
                return response
    else:
        if (tmpuser.fourtytwo == False):
            form = EditProfileUserForm(request.POST, request.FILES, instance=tmpuser)
        else:
            form = EditProfile42UserForm(request.POST, request.FILES, instance=tmpuser)
        if (form.is_valid()):
                formtmp = form.save(commit=False)
                if (tmpuser.fourtytwo == True):
                      formtmp.save()
                      response = render(request, 'main_root.html', {'User': tmpuser})
                      return response
                else:
                    formtmp.password = hashlib.sha256(str(request.POST['password']).encode('utf-8')).hexdigest()
                    formtmp.save()
                    ##add / to url of avatar
                    tmpuser =  User.objects.get(email=formtmp.email)
                    if tmpuser.avatar and ('http' not in str(tmpuser.avatar)) and not str(tmpuser.avatar).startswith('/'):
                           tmpuser.avatar = '/' + str(tmpuser.avatar)
                           tmpuser.save()
                    ##end add / to url of avatar
                response = render(request, 'main_root.html', {'User': tmpuser})
                return response
        else:
              if (tmpuser.fourtytwo == False):
                    form = EditProfileUserForm(request.POST, request.FILES, instance=tmpuser)
              else:
                    form = EditProfile42UserForm(request.POST, request.FILES, instance=tmpuser)
              response = render(request, 'main_newuser.html', {'form': form, 'User': tmpuser, 'Data': FormData})
              return response

## Logoff ##

def logoffPage(request):
       response = render(request, 'main_root.html')
       response.set_cookie('tokenid', '')
       return response

## Login ##
FormDataLogin = {'ErrorMsg': '', 'URL42': os.environ["URL42"]}
def loginPage(request):
    if not request.method == 'POST':
           try:
                token = request.COOKIES.get('tokenid')
                tmpuser = get_user_from_token(token)
           except:
                  tmpuser = ''
           form = LoginUserForm()
           response = render(request, 'main_login.html', {'form': form, 'User': tmpuser, 'Data': FormDataLogin})
           return response
    else:
           try:
                  tmpuser = User.objects.get(email=request.POST['email'])
                  if (tmpuser.password == hashlib.sha256(str(request.POST['password']).encode('utf-8')).hexdigest()):
                        if (tmpuser.tfa == False):
                            response = render(request, 'main_root.html', {'User': tmpuser})
                            refresh = get_tokens_for_user(tmpuser)
                            tokenid = str(refresh)
                            tmpuser.tokenid = tokenid
                            tmpuser.save()
                            response.set_cookie('tokenid', tokenid, secure=True, httponly=True)
                            return response
                        else:
                            return tfa(request, tmpuser)
                  else:
                    FormDataLogin['ErrorMsg'] = 'The password is wrong'
                    form = LoginUserForm(request.POST)
                    form.errors['email'] = form.error_class()
                    form.errors['password'] = form.error_class()
                    response = render(request, 'main_login.html', {'form': form, 'Data': FormDataLogin, 'Data': FormDataLogin})
                    return response
           except:
                  FormDataLogin['ErrorMsg'] = 'The indicated email is not registered as a user'
                  form = LoginUserForm(request.POST)
                  form.errors['email'] = form.error_class()
                  form.errors['password'] = form.error_class()
                  response = render(request, 'main_login.html', {'form': form, 'Data': FormDataLogin})
                  return response

## Main page ##

def mainPage(request):
    try:
        token = request.COOKIES.get('tokenid')
        tmp = get_user_from_token(token)
        response = render(request, 'main_index.html', {'User': tmp})
        return response
    except:
        return HttpResponseRedirect("welcome")
        
## New user section ##

#Dictionary for the new user form
FormData = {'Action': '', 'SecurityCode': 'input type=text name=securitycode maxlength=10 required="required"', 'TopMsg': '', 'ErrorMsg': ''}
#New user form asking for your email address
def newUserEmailform(request, error = ''):
        try:
               tmpuser = User.objects.get(tokenid=request.COOKIES.get('tokenid'))
        except:
            tmpuser = ''
        FormData['Action'] = 'Check Email'
        FormData['SecurityCode'] = 'input type=hidden name=securitycode maxlength=10'
        FormData['TopMsg'] = 'Specify with which email address you want to register.'
        FormData['ErrorMsg'] = error
        form = NewUserForm()
        form.fields['password'].widget = forms.HiddenInput()
        form.fields['displayname'].widget = forms.HiddenInput()
        form.fields['avatar'].widget = forms.HiddenInput()
        response = render(request, 'main_newuser.html', {'form': form, 'Data': FormData, 'User': tmpuser})
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
        response = render(request, 'main_newuser.html', {'form': form, 'Data': FormData})
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
                        formtmp = form.save(commit=False)
                        formtmp.password = hashlib.sha256(str(request.POST['password']).encode('utf-8')).hexdigest()
                        formtmp.save()
                        ##add / to url of avatar
                        tmpuser =  User.objects.get(email=formtmp.email)
                        if (str(tmpuser.avatar) != ''):
                            tmpuser.avatar = '/' + str(tmpuser.avatar)
                            tmpuser.save()
                        ##end add / to url of avatar
                        refresh = RefreshToken.for_user(tmpuser)
                        tokenid = str(refresh.access_token)
                        tmpuser.tokenid = tokenid
                        tmpuser.totp_secret = pyotp.random_base32()
                        tmpuser.save()
                        response = render(request, 'main_root.html', {'User': tmpuser})
                        response.set_cookie('tokenid', tokenid, secure=True, httponly=True)
                        return response
        except:
                return HttpResponseRedirect("/")      
        FormData['Action'] = 'Create User'
        FormData['SecurityCode'] = 'input type=hidden name=securitycode maxlength=10 value=' + request.POST['securitycode']
        FormData['TopMsg'] = request.POST['email']
        form.fields['email'].widget = forms.HiddenInput()
        response = render(request, 'main_newuser.html', {'form': form, 'Data': FormData})
        return response

def AnonimousUser(request):
    try:
        characters = string.ascii_letters + string.digits
        tmpusername = 'A' + ''.join(random.choice(characters) for i in range(6))
        tmpuser = User()
        tmpuser.email = tmpusername + '@pong42.com'
        tmpuser.displayname = tmpusername
        tmpuser.password = hashlib.sha256(str(tmpusername).encode('utf-8')).hexdigest()
        tmpuser.save()
        refresh = RefreshToken.for_user(tmpuser)
        tokenid = str(refresh.access_token)
        tmpuser.tokenid = tokenid
        tmpuser.save()
        response = render(request, 'main_root.html', {'User': tmpuser})
        response.set_cookie('tokenid', tokenid, secure=True, httponly=True)
        return response
    except:
        return HttpResponseRedirect("/")

def urlavatar(ori):
    avatar = str(ori)
    if not avatar.find('static/avatars'):
         avatar = '/' + avatar
    return avatar