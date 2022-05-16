from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm

User = get_user_model()


class GroupChangeForm(UserChangeForm):
    """Overriding visible fields."""
    password = None

    class Meta:
        model = User
        fields = ('groups',)
