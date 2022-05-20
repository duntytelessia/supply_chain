from django.contrib.auth import get_user_model
from django.forms import ModelForm
from django import forms
from django.core.exceptions import ValidationError
from data.models import Order, Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['quanT', ]
        labels = {'quanT': ''}

