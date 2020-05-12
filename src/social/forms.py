from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(label='Username', max_length=16, required=True)
    password = forms.CharField(label='Password', max_length=16, required=True, widget=forms.PasswordInput)
    first_name = forms.CharField(label='First Name', max_length=64, required=True)
    last_name = forms.CharField(label='Last Name', max_length=64, required=True)

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=16, required=True)
    password = forms.CharField(label='Password', max_length=16, required=True, widget=forms.PasswordInput)

class EditProfileForm(forms.Form):
    password = forms.CharField(label='Password', max_length=16, widget=forms.PasswordInput, required=False, empty_value="")
    first_name = forms.CharField(label='First Name', max_length=64, required=False, empty_value="")
    last_name = forms.CharField(label='Last Name', max_length=64, required=False, empty_value="")
    about = forms.CharField(label="About", required=False , widget=forms.Textarea)
    profile_picture_from_file = forms.ImageField(label="Upload a Picture", required=False)
    profile_picture_from_url = forms.CharField(label='Or choose a Picture from an URL', required=False, empty_value="")
    #TODO List of user uploaded files
