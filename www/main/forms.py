from django import forms
from .models import User

class NewUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email', 'password', 'displayname', 'avatar')

class LoginUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email', 'password')
        