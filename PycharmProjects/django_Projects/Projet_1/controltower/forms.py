from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from data.models import Goods

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
