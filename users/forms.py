from django import forms
from users.models import Account
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Enter password",
        widget=forms.PasswordInput(attrs={
            'class':'pass_log_id', 
            'type':'password',
            'placeholder':'Enter password'
        }),
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={
            'class':'pass_log_id', 
            'type':'password',
            'placeholder':'Confirm password'
        }),
    )

    class Meta:
        model = Account
        fields = ('email', 'name', 'password1', 'password2')
        widgets = {
            'name':forms.TextInput(attrs={
                'placeholder': 'First Name',
                'autofocus': ''
            }),
            'email':forms.EmailInput(attrs={
                'placeholder': 'Email address',
                'autofocus': 'off'
            }),
        }

class LoginForm(forms.ModelForm):
    password = forms.CharField(
        label="Enter password",
        widget=forms.PasswordInput(attrs={
            'class':'pass_log_id', 
            'type':'password',
            'placeholder':'Enter password'
        }),
    )
    class Meta:
        model  =  Account
        fields =  ('email', 'password')
        widgets = {
            'email':forms.TextInput(attrs={
                'placeholder': 'Your email',
            }),
        }

    def clean(self):
        if self.is_valid():

            email = self.cleaned_data.get('email')
            password = self.cleaned_data.get('password')
            if not authenticate(email=email, password=password):
                raise forms.ValidationError('Invalid Login')