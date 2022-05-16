from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django import forms
from django.core.exceptions import ValidationError

User = get_user_model()


class CustomUserCreationForm(forms.Form):  # Creation new user
    username = forms.CharField(label='Enter Username', max_length=150)
    firstname = forms.CharField(label='Enter First Name', max_length=150, required=False)
    lastname = forms.CharField(label='Enter Last Name', max_length=150, required=False)
    email = forms.EmailField(label='Enter email')
    password1 = forms.CharField(label='Enter password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    def clean_username(self):   # verifying that username is valid
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise ValidationError("Username already exists")
        return username

    def clean_email(self):  # verifying that email is valid
        email = self.cleaned_data['email'].lower()
        r = User.objects.filter(email=email)
        if r.count():
            raise ValidationError("Email already exists")
        return email

    def clean_password2(self):  # verifying that two passwords are the same
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Password don't match")

        return password2

    def save(self, commit=True):    # saves the new user in the database
        user = User.objects.create_user(
            self.cleaned_data['username'],  # cleaned_date = security, blocks any information that could be dangerous
            self.cleaned_data['email'],
            self.cleaned_data['password1'],
            first_name=self.cleaned_data['firstname'],
            last_name=self.cleaned_data['lastname']
        )
        return user


class UserChangeForm(forms.ModelForm):  # Modify the info of a user
    """Overriding visible fields."""

    class Meta:  # choses the information that can be changed
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class ValidationForm(forms.ModelForm):  # Allow the user to validate his class
    class Meta:
        model = User
        fields = ['validate']
