# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$

from django.urls import path

from .views import accept

app_name = 'esiidm'

urlpatterns = [
    path('accept/<otp>', accept, name='accept'),
]
