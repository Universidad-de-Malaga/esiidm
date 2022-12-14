# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$
"""
This a module for auxiliary and utility funcions or classes
for the ESI IdM
"""

from django.conf import settings

def get_setting(name, default=None):
    # None is the default default, just in case :-)
    return getattr(settings, name, default)
