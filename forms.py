# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

class cardLoadForm(forms.Form):
    delimiter = forms.ChoiceField(label=_('Select delimiter your file uses'),
                                  initial=',',
                                  choices=[(',',_('comma ","')),
                                           (';',_('semi-colon ";"'))])
    data = forms.FileField(label=_('Data file:'))

class heiLoadForm(forms.Form):
    delimiter = forms.ChoiceField(label=_('Select delimiter your file uses'),
                                  initial=',',
                                  choices=[(',',_('comma ","')),
                                           (';',_('semi-colon ";"'))])
    data = forms.FileField(label=_('Data file:'))

class officerLoadForm(forms.Form):
    delimiter = forms.ChoiceField(label=_('Select delimiter your file uses'),
                                  initial=',',
                                  choices=[(',',_('comma ","')),
                                           (';',_('semi-colon ";"'))])
    data = forms.FileField(label=_('Data file:'))


