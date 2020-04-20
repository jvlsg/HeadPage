from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(label='Username', max_length=16, required=True)
    password = forms.CharField(label='Password', max_length=16, required=True, widget=forms.PasswordInput)
    first_name = forms.CharField(label='First Name', max_length=64, required=True)
    last_name = forms.CharField(label='Last Name', max_length=64, required=True)