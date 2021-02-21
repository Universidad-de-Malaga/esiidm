# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$
"""
   We define functions for receving signals from objects here
"""

from django.core.signing import TimestampSigner
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail,EmailMessage

from .models import Person, StudentCard, HEI

# Boilerplate for signal processing code
#@receiver(signal,sender=Object,dispatch_uid="Name")
#def emiteRemesa(sender,instance, *args, **kwargs):
#    """
#    Docstring
#    """
#    do whatever
#    return
