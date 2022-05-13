from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import ValidationError


class GroupChangeForm(UserChangeForm):
    """Overriding visible fields."""
    password = None

    class Meta:
        model = User
        fields = ('groups',)
