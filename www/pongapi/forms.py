from django import forms
from .models import User

class NewUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email', 'password', 'displayname', 'avatar')

class LoginUserForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'style': 'width: 300px; height: 40px;'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'style': 'width: 300px; height: 40px;'}))

    class Meta:
        model = User
        fields = ('email', 'password')
        
class EditProfileUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email', 'password', 'displayname', 'avatar', 'tfa', 'tfa_type', 'phone_number')
    def clean(self):
        cleaned_data = super().clean()
        tfa = cleaned_data.get('tfa')
        tfa_type = cleaned_data.get('tfa_type')
        phone_number = cleaned_data.get('phone_number')
        if tfa and tfa_type == 2 and not phone_number:
             self.add_error('phone_number', 'Phone number cannot be blank when tfa_type is SMS')
        return cleaned_data
        
class EditProfile42UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('tfa', 'tfa_type', 'phone_number')
    def clean(self):
        cleaned_data = super().clean()
        tfa = cleaned_data.get('tfa')
        tfa_type = cleaned_data.get('tfa_type')
        phone_number = cleaned_data.get('phone_number')
        if tfa and tfa_type == 2 and not phone_number:
             self.add_error('phone_number', 'Phone number cannot be blank when tfa_type is SMS')
        return cleaned_data
        