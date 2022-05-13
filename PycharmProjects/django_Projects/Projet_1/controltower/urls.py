from django.urls import path
from controltower.views import interface, change_group, del_user

urlpatterns = [
    path('', interface, name='interface'),
    path('cg/<str:username>', change_group, name='change_group'),
    path('del/<str:username>', del_user, name='del_user') # variable type mandatory
]
