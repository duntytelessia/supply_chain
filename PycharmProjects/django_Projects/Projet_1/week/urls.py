from django.urls import path

from week.views import *

urlpatterns = [
    path('', week, name='week'),
    path('notallowed/', notallowed, name='notallowed'),
    path('<int:week>/controltower/modify', modify_as_controltower, name='modify_as_controltower'),
    path('<int:week>/controltower/view', view_as_controltower, name='view_as_controltower'),
    path('<int:week>/<str:username>', actor, name='actor'),
    path('<int:week>/<str:username>/L', actorL, name='actorL'),
]
