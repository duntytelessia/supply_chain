from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django import forms
from django.core.exceptions import ValidationError

User = get_user_model()

class CustomUserCreationForm(forms.Form):
    username = forms.CharField(label='Enter Username', max_length=150)
    firstname = forms.CharField(label='Enter First Name', max_length=150, required=False)
    lastname = forms.CharField(label='Enter Last Name', max_length=150, required=False)
    email = forms.EmailField(label='Enter email')
    password1 = forms.CharField(label='Enter password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
    #group = forms.ModelChoiceField(label='Actor Category', queryset=Group.objects.all())

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise  ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = User.objects.filter(email=email)
        if r.count():
            raise  ValidationError("Email already exists")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Password don't match")

        return password2

    def save(self, commit=True):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password1'],
            first_name=self.cleaned_data['firstname'],
            last_name=self.cleaned_data['lastname']
        )
        #if self.cleaned_data['group'] is not None:
        #    my_group = Group.objects.get(name=self.cleaned_data['group'])
        #    my_group.user_set.add(user)
        return user


class UserChangeForm(forms.Form):
    """Overriding visible fields."""
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')


class ValidationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['validate']