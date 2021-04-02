# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$

from django.urls import path
from django.urls import re_path

from .views import accept, authenticate, start
from .auth import authn

app_name = 'esiidm'

urlpatterns = [
    path('accept/<otp>', accept, name='accept'),
    re_path('accept/<otp>/(?P<response>[YN])', accept, name='accept'),
    path('authenticate', authenticate, name='authenticate'),
    path('authn/<method>', authn, name='authn'),
]
