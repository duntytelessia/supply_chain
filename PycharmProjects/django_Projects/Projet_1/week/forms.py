from django.contrib.auth import get_user_model
from django.forms import ModelForm
from django import forms
from django.core.exceptions import ValidationError
from data.models import CustomUser

User = get_user_model()


class ChangeUser_1(ModelForm):
    password = None

    class Meta:
        model = User
        fields = ('funds', 'validate', 'maxT')


class ChangeUser(ModelForm):
    password = None

    class Meta:
        model = User
        fields = ('validate', )


