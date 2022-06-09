from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from data.models import Goods, Worker
from django.core.exceptions import ValidationError
from django import forms

User = get_user_model()

# form to change the group of a user
class GroupChangeForm(UserChangeForm):
    """Overriding visible fields."""
    password = None

    class Meta:
        model = User
        fields = ('groups',)


class GoodChangeForm(UserChangeForm):
    """Overriding visible fields."""
    password = None

    class Meta:
        model = Goods
        fields = ('nameG', 'durG',)


class GoodChangeForm_1(UserChangeForm):
    """Overriding visible fields."""
    password = None

    class Meta:
        model = Goods
        fields = ('nameG', 'durG', 'coefG')

    def clean(self):
        cleaned_data = super(GoodChangeForm_1, self).clean()
        if any(self.errors):
            return

        coef = self.cleaned_data['coefG']
        if coef <= 0:
            raise ValidationError("coeficient can't be lower than 0")

class WorkersForm(UserChangeForm):

    password = None

    class Meta:
        model = Worker
        fields = ('eff', 'sal',)


