# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$
"""
We define functions for receving signals from objects here.
It has to be imported in models.py, better at the end.
"""

from django.core.signing import TimestampSigner
from django.db.models.signals import pre_save, post_save
from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail,EmailMessage

from .models import Person, StudentCard, HEI, Officer


# Boilerplate for signal processing code
#@receiver(signal, sender = Object, dispatch_uid = "Name")
#def uniqueFunctionName(sender, instance, *args, **kwargs):
#    """
#    Docstring
#    """
#    do whatever
#    return

@receiver(post_delete, sender = Officer, dispatch_uid = "CleanOfficers")
@receiver(post_delete, sender = StudentCard, dispatch_uid = "CleanStudents")
def clean_persons(sender, instance, *args, **kwargs):
    """
    Signal processor for removing students when they have no other links
    """
    if sender == StudentCard: person = instance.student
    if sender == Officer: person = instance.person
    if person.is_superuser: return
    if sender == StudentCard and person.is_officer: return
    # There are no roles left
    if not person.is_student: person.delete()
    return

