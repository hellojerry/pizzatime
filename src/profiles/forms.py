from django import forms
from .models import UserProfile, ZipData
from orders.models import Order
from localflavor.us.forms import USZipCodeField, USStateField, USPhoneNumberField

from django.contrib.auth import get_user_model

from django.contrib.auth.hashers import make_password

import csv

User = get_user_model()

class CheckAddressForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('street_address','city','state','zipcode')

    
    
class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    form_tag = forms.CharField(widget=forms.HiddenInput)
    
    def clean(self):
        password = self.cleaned_data['password']
        email = self.cleaned_data['email']
        user = User.objects.get(email=email)
        if not user.check_password(password):
            raise forms.ValidationError("This password is incorrect")
        return self.cleaned_data



    
    
class RegisterForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ['user', 'role', 'street_address', 'city', 'state', 'zipcode']
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    form_tag = forms.CharField(widget=forms.HiddenInput)

    def clean_username(self):
        username = self.cleaned_data['email']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username %s already exists.' % (username))  
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email %s already exists.' % (email))  
        return email
    
    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password == password2:
            final_password = make_password(password)
            del cleaned_data['password']
            del cleaned_data['password2']
            cleaned_data['password'] = final_password
            cleaned_data['password2'] = final_password
        
        if password != password2:
            self.errors['password'] = self.error_class(['Passwords do not match!'])
            #raise forms.ValidationError("Please make sure your passwords match!")
            del cleaned_data['password']
            del cleaned_data['password2']
        return cleaned_data   
    
    
    
    
class ZipInput(forms.Form):
    file = forms.FileField()

