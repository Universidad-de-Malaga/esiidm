# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
<<<<<<< HEAD
<<<<<<< HEAD
# $Id$
=======
=======
>>>>>>> 0f5e2f2 (is_ functions for persons)
# $Id$

>>>>>>> f9b7c3d (First version of models)
from django.db import models
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.core.signing import TimestampSigner
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser
AbstractUser._meta.get_field('email')._unique = True

import uuid

# Create your models here.

class HEI(models.Model):
    """A class for describing a High Education Institution
    These will be the root for administrators and students
    """

    name = models.CharField(max_length = 100,
                            db_index = True,
                            verbose_name = _('Institution name'))
    url = models.URLField(max_length = 256,
                           db_index = True,
                           blank = True,
                           null = True,
                           verbose_name = _('Institution web site'))
    pic = models.CharField(max_length = 20,
                           db_index = True,
                           unique = True,
                           verbose_name = _('PIC code'))
    euc = models.CharField(max_length = 50,
                           db_index = True,
                           unique = True,
                           verbose_name = _('EUC code'))
    erc = models.CharField(max_length = 30,
                           db_index = True,
                           unique = True,
                           verbose_name = _('Erasmus code'))
    sho = models.CharField(max_length = 100,
                           db_index = True,
                           unique = True,
                           verbose_name = _('SCHAC Home Organization'),
                           help_text = _('Your Internet domain. Needed for ESI'))

    class Meta:
        verbose_name = _('Higher Education Institution')
        verbose_name_plural = _('Higher Education Institutions')


class Person(AbstractUser):
    """A class for describing persons that belong to a HEI"""

    username = None  # We are not going to use usernames

    identifier = models.CharField(max_length = 300,
                                  db_index = True, blank=True, null=True,
                                  verbose_name = _('Government issued identifier'))

    # Control information
    managedBy = models.ForeignKey('self',
                                  on_delete = models.PROTECT,
                                  db_index = True,
                                  default = 1,
                                  verbose_name = _('Responsible person'))
    createdOn = models.DateTimeField(_('Created on'),
                                     auto_now_add = True,
                                     db_index = True,
                                     editable = False)
    modifiedOn = models.DateTimeField(_('Modified on'),
                                      auto_now = True,
                                      db_index = True,
                                      editable = False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')
        index_together = ['email', 'identifier']
        #constraints = [
        #    models.UniqueConstraint(fields=['email', 'identifier'],
        #                            name='one_email_per_identifier'),
        #]

    def is_officer(self):
        return len(self.heis.all()) > 0

    def is_student(self):
        return len(self.cards.all()) > 0


class StudentCard(models.Model):
    """A class for describing student cards.
    Links persons to institutions as students.
    """

    student = models.ForeignKey(Person,
                                on_delete = models.CASCADE,
                                db_index = True, 
                                related_name = 'cards',
                                related_query_name = 'card',
                                verbose_name = _('Student who owns the card'))
    hei = models.ForeignKey(HEI,
                            on_delete = models.CASCADE,
                            verbose_name = _("Person's HEI"))
    esc = models.CharField(max_length = 300,
                           db_index = True, 
                           unique = True,
                           verbose_name = _('European Student Card number'))
    esi = models.CharField(max_length = 300,
                           db_index = True, 
                           unique = True,
                           verbose_name = _('Student specific part of ESI'),
                           help_text = 'ESI: European Student Identifier')

    # Control information
    manager = models.ForeignKey(Person,
                                on_delete = models.PROTECT,
                                verbose_name = _('Responsible person'))
    createdOn = models.DateTimeField(_('Created on'),
                                     auto_now_add = True,
                                     db_index = True,
                                     editable = False)
    modifiedOn = models.DateTimeField(_('Modified on'),
                                      auto_now = True,
                                      db_index = True,
                                      editable = False)


    class Meta:
        verbose_name = _('Card')
        verbose_name_plural = _('Cards')
        index_together = ['esi', 'hei', 'student']
        constraints = [
            models.UniqueConstraint(fields=['esi', 'hei', 'student'], name='card_unique')
        ]

class Officer(models.Model):
    """A class for linking persons to the institutions they manage"""

    person = models.ForeignKey(Person,
                               on_delete = models.DO_NOTHING,
                               db_index = True, 
                               related_name = 'heis',
                               related_query_name = 'hei',
                               verbose_name = _('Person that manages a HEI'))
    hei = models.ForeignKey(HEI,
                            on_delete = models.CASCADE,
                            db_index = True, 
                            related_name = 'managers',
                            related_query_name = 'manager',
                            verbose_name = _("Managed HEI"))

    # Control information
    manager = models.ForeignKey(Person,
                                on_delete = models.PROTECT,
                                verbose_name = _('Responsible person'))
    createdOn = models.DateTimeField(_('Created on'),
                                     auto_now_add = True,
                                     db_index = True,
                                     editable = False)
    modifiedOn = models.DateTimeField(_('Modified on'),
                                      auto_now = True,
                                      db_index = True,
                                      editable = False)


    class Meta:
        verbose_name = _('Officer')
        verbose_name_plural = _('Officers')
        index_together = ['person', 'hei']
        constraints = [
            models.UniqueConstraint(fields=['person', 'hei'], name='manager_unique')
        ]

