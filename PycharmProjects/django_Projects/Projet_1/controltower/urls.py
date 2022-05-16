from django.urls import path
from controltower.views import interface, change_group, del_user, valid

urlpatterns = [
    path('', interface, name='interface'),  # main page of control tower
    path('cg/<str:username>', change_group, name='change_group'),   # change the group of user: username
    path('del/<str:username>', del_user, name='del_user'),# variable type mandatory, delet user: username
    path('valid/', valid, name='valid')     # when admin has validated all actors
]
