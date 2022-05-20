from django.contrib.auth import get_user_model
from django.forms import ModelForm
from django import forms
from django.core.exceptions import ValidationError
from data.models import Order, Transaction


class PriceForm(forms.Form):

    price = forms.IntegerField(min_value=0)

    def save(self, good, week, seller):
        to_modify = Transaction.objects.filter(goods__exact=good, dateT=week, sellerT=seller)
        for t in to_modify:
            t = Transaction(priceT=self.cleaned_data['price'])
            t.save()
