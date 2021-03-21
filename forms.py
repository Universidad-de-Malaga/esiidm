# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$

from django import forms
from django.conf import settings

class cardLoadForm(forms.Form):
    data = forms.FileField()

class heiLoadForm(forms.Form):
    data = forms.FileField()

class officerLoadForm(forms.Form):
    data = forms.FileField()


