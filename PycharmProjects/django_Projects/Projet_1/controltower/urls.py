from django.urls import path
from controltower.views import *

urlpatterns = [
    path('', interface, name='interface'),  # main page of control tower
    path('cg/<str:username>', change_group, name='change_group'),   # change the group of user: username
    path('del/<str:username>', del_user, name='del_user'),  # variable type mandatory, delet user: username
    path('valid/', valid, name='valid'),    # when admin has validated all actors
    path('valid/<str:idg>', edit_good, name='edit_good'),# to edit data of the good: idG
    path('validate_all', validate_all, name='validate_all'),
    path('begin_simulation', begin_simulation, name='begin_simulation'),
    path('new_week', new_week, name='new_week'),
    path('costs', costs, name='costs'),
    path('kpi', kpi, name='kpi'),
    path('confirmation', confirmation, name='confirmation'),
    path('delete', delete, name='delete'),
]
