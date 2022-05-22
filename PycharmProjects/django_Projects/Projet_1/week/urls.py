from django.urls import path
from week.views import *

from week.views import modify_as_controltower, week, notallowed

urlpatterns = [
    path('', week, name='week'),
    path('notallowed/', notallowed, name='notallowed'),
    path('<int:week>/controltower/modify', modify_as_controltower, name='modify_as_controltower'),
    path('<int:week>/controltower/endpoint1', modify_as_controltower, name='modify_as_controltower'),
    path('<int:week>/controltower/endpoint2', modify_as_controltower, name='modify_as_controltower'),
]
