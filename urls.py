# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$

from django.urls import path
from django.urls import re_path

from .views import accept, authenticate, start, reinvite, end
from .auth import authn

app_name = 'esiidm'

urlpatterns = [
    path('reinvite', reinvite, name='reinvite'),
    re_path(r'accept/(?P<token>[^/]+)/(?P<response>[YN])', accept, name='accept'),
    path('accept/<token>', accept, name='accept'),
    path('authenticate', authenticate, name='authenticate'),
    path('accounts/login/', authenticate, name='login'),
    path('logout/', end, name='logout'),
    path('authn/<method>', authn, name='authn'),
    path('', start, name='start'),
]
