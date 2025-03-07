# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$

from django.urls import path
from django.urls import re_path

from .views import (
    accept,
    authenticate,
    start,
    reinvite,
    end,
    cards,
    namelist,
    statistics,
    TheAPI,
)
from .auth import authn

app_name = 'esiidm'

urlpatterns = [
    path('reinvite', reinvite, name='reinvite'),
    path('cards/<int:hid>', cards, {'blank': False}, name='cards'),
    path('cards/<int:hid>/blank', cards, {'blank': True}, name='cards'),
    re_path(
        r'accept/(?P<token>[^/]+)/(?P<response>[YN])', accept, name='accept'
    ),
    path('accept/<token>', accept, name='accept'),
    path('authenticate', authenticate, name='authenticate'),
    path('accounts/login/', authenticate, name='login'),
    path('logout/', end, name='logout'),
    path('authn/<method>', authn, name='authn'),
    re_path('authn/(?P<method>[^/]+)/.*', authn, name='authn'),
    path('stats/', statistics, name='stats'),
    path('names/', namelist, name='names'),
    path('api/<sho>', TheAPI.as_view(), name='api'),
    path('api/<sho>/<esi>', TheAPI.as_view(), name='api'),
    path('api/<sho>/<esi>/<deltoken>', TheAPI.as_view(), name='api'),
    path('', start, name='start'),
]
