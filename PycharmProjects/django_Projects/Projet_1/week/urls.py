from django.urls import path
from week.views import *

urlpatterns = [
    path('', week, name='week'),
    path('notallowed/', notallowed, name='notallowed'),
    path('<int:week>/controltower/modify', modify_as_controltower, name='modify_as_controltower'),
    path('<int:week>/<str:username>', infos, name='modify'),
    path('<int:week>/<str:username>/stock/Suppliers_A', stock_supp_a, name='stock_supp_a')
]
