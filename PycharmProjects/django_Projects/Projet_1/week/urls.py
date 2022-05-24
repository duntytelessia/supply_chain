from django.urls import path

from week.views import *

urlpatterns = [
    path('', week, name='week'),
    path('notallowed/', notallowed, name='notallowed'),
    path('<int:week>/controltower/modify', modify_as_controltower, name='modify_as_controltower'),
    path('<int:week>/Suppliers_A/<str:username>', supp_a, name='supp_a'),
]
