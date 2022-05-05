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
from django.core.mail import EmailMessage
from django.core.signing import TimestampSigner
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as pgettext
from django.utils import timezone
from django.template.loader import render_to_string
from django_countries.fields import CountryField
from django.contrib.auth.models import AbstractUser
AbstractUser._meta.get_field('email')._unique = True

from urllib import parse
from fpdf import FPDF
import uuid
import requests
import calendar
import qrcode
import io
import base64
import os

from .utils import get_setting

# Create your models here.

class Person(AbstractUser):
    """A class for describing persons"""

    username = None  # We are not going to use usernames
    identifier = models.CharField(max_length = 300,
                          db_index = True, blank=True, null=True,
                          verbose_name = _('Government issued identifier'))

    # Control information
    otp = models.CharField(max_length = 36,
                           db_index = True,
                           verbose_name = _('Invitation code'),
                           default = uuid.uuid4,
                           editable = False)
    managedBy = models.ForeignKey('self',
                                  on_delete = models.PROTECT,
                                  db_index = True,
                                  default = 1,
                                  related_name = 'persons',
                                  related_query_name = 'person',
                                  verbose_name = _('Responsible person'))
    createdOn = models.DateTimeField(verbose_name = _('Created on'),
                                     auto_now_add = True,
                                     db_index = True,
                                     editable = False)
    modifiedOn = models.DateTimeField(verbose_name = _('Modified on'),
                                      auto_now = True,
                                      db_index = True,
                                      editable = False)
    invitedOn = models.DateTimeField(verbose_name = _('Invited on'),
                                     null = True,
                                     blank = True,
                                     db_index = True)
    acceptedOn = models.DateTimeField(verbose_name = _('Accepted on'),
                                      null = True,
                                      blank = True,
                                      db_index = True)

    # It is possible to override the defaults in settings.py
    USERNAME_FIELD = get_setting('PERSON_USERNAME_FIELD', 'email')
    REQUIRED_FIELDS = get_setting('PERSON_REQUIRED_FIELDS', [])

    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')
        index_together = ['email', 'identifier']
        ordering = ['last_name', 'first_name']
        constraints = [
            models.UniqueConstraint(fields=['email', 'identifier'],
                                    name='one_email_per_identifier'),
        ]

    def __str__(self):
        return f'{self.last_name}, {self.first_name} <{self.email}>'

    @property
    def is_officer(self):
        return Officer.objects.filter(person=self).exists()

    @property
    def is_student(self):
        return StudentCard.objects.filter(student=self).exists()

    @property
    def has_accepted(self):
        return self.acceptedOn is not None

    @property
    def is_pending(self):
        return self.acceptedOn is None and self.invitedOn is not None

    @property
    def is_invited(self):
        return self.invitedOn is not None

    @property
    def myESI(self):
        """
        Returns all ESI associated to a Person for generating the required
        schacPersonalUniqueCode attrbute values in the SAML assertions.
        """
        return [c.myESI(myacid=True) for c in self.cards.all()]

    @property
    def myHEI(self):
        # The most common use case is "one Person <-> one HEI", 
        # so we return the first HEI
        if self.is_officer: return self.manages.first().hei
        if self.is_student: return self.cards.first().hei
        # Just in case person is not associated to a certain HEI
        return None

    @property
    def HEIs(self):
        # Officers may manage more than one HEI, we need them as QuerySet
        if not self.is_officer: return HEI.objects.none()
        # List of HEIs the person is an Officer for
        heis = [o.hei.id for o in self.manages.all()]
        return HEI.objects.filter(id__in=heis)

    @property
    def affiliation(self):
        # Return scoped affiliations for the person
        result = []
        if self.is_student:
            result += [f'student@{c.hei.sho}' for c in self.cards.all()]
        if self.is_officer:
            result += [f'staff@{o.hei.sho}' for o in self.manages.all()]
        return result

    #def save(self, *args, **kwargs):
    #    """
    #    We do some checks before saving
    #    """
    #    # How long has lapsed since last invitation?
    #    # Nobody is so fast to reject the invitation in less than a minute
    #    d = 0
    #    if self.invitedOn is not None:
    #        d = timezone.now() - self.invitedOn
    #        d = d.seconds
    #    # In case someone decides to remove consent, we remove the cards
    #    if d > 60 and not self.has_accepted and self.cards.count() > 0:
    #        for card in self.cards.all(): card.delete()
    #    # If someone has consented and there are unregistered associated cards
    #    for card in self.cards.filter(registeredOn__isnull=True):
    #        # Send the information to the ESC Router
    #        card.save_in_ESCR()
    #    super(Person, self).save(*args, **kwargs)
            
    def delete(self, *args, **kwargs):
        """
        Delete cards before removing the person
        """
        for card in self.cards.all(): card.delete()
        # If there are cards left, something went wrong
        # we cannot delete the person
        if self.is_student: return
        super(Person, self).delete(*args, **kwargs)

    def invite(self, manager=None, hei=None, subject=None,
               host=settings.ALLOWED_HOSTS[0],
               template='esiidm/student_invite.txt'):
        """
        Send an invitation with a personalised time limited link.
        The attribute value obtained from the IdSource used for accessing
        the aceptance view will be linked to this person as
        a verified Identifier.
        - manager : is the person that is creating the invitation.
        - subject : an alternative subject, just in case
        - hei : A HEI object, if we want the message to be in its name
        """
        signer = TimestampSigner()
        context = {
                    'who': '{} {}'.format(self.first_name, self.last_name),
                    'manager': manager,
                    'hei': hei,
                    'host': host,
                    'link': reverse('esiidm:accept',
                                    kwargs={'token': signer.sign(self.otp)}),
                  }
        msg = EmailMessage()
        msg.to = [f'"{self.first_name} {self.last_name}" <{self.email}>']
        msg.from_email = f'ESI IdM at {host}<no-reply@{host}>'
        if manager is not None:
            msg.from_email = '{} {} <no-reply@{}>'.format(manager.first_name,
                                                          manager.last_name,
                                                          host)
        if hei is not None:
            msg.from_email = f'"{hei.name}" <no-reply@{host}>'
        msg.subject = _('Consent is required for the Student Card System')
        if subject is not None: msg.subject = subject
        if manager is not None:
            # Replies should go to the inviting person
            msg.reply_to = ['"{} {}" <{}>'.format(manager.first_name,
                                                  manager.last_name,
                                                  manager.email)]
        msg.extra_headers = {'Message-Id': '{}@esiidm'.format(uuid.uuid4())}
        msg.body = render_to_string(template, context=context)
        try:
            msg.send()
            self.invitedOn = timezone.now()
            self.save()
            return True
        except:
            # Invite could not be sent
            return False


class IdSource(models.Model):
    """
    A class for managing authentication sources.
    It is designed for offering a simple interface to display information
    about available authentication sources in the system and an easy way
    for activating and deactivating them.
    The relevant attributes for objects of this class are:
    - Source: a string that identifies the source in the system
    - Attribute: the attribute providing the value that links to a person
    - Extractor: a regular expression for extracting the value that
                 will be used to identify a given individual
    - Active: If the source is active or not
    - Description: Descriptive information about the authentication source
    """

    source = models.CharField(
                        max_length = 25,
                        db_index = True,
                        unique = True,
                        editable = False,
                        verbose_name = _('Source name'))
    attribute = models.CharField(
                           max_length = 100,
                           default = 'ANY',
                           db_index = True,
                           editable = False,
                           verbose_name = _('Attribute name'))
    extractor = models.CharField(
                           max_length = 200,
                           default = '.*',
                           editable = False,
                           verbose_name = _('Extractor'),
                           help_text = _(
                              'Regular expression for extracting the value.'))
    active = models.BooleanField(
                           default = False,
                           db_index = True,
                           verbose_name = _('Active'),
                           help_text = _('Is the source active?'))
    description = models.CharField(
                             max_length = 200,
                             default = 'Authentication source',
                             editable = True,
                             verbose_name = _('Description'),
                             help_text = _(
                                'Authentication source description.'))


    # Control data
    createdOn = models.DateTimeField(verbose_name = _('Created on'),
                                     auto_now_add = True,
                                     db_index = True,
                                     editable = False)
    modifiedOn = models.DateTimeField(verbose_name = _('Modified on'),
                                      auto_now = True,
                                      db_index = True,
                                      editable = False)

    class Meta:
        verbose_name = _('Authentication source')
        verbose_name_plural = _('Authentication sources')
        #index_together = ['source', 'attribute']
        ordering = ['active', 'source', 'attribute']
        constraints = [
            models.UniqueConstraint(fields=['source', 'attribute'],
                                    name='one_attribute_per_source'),
        ]

    def __str__(self):
        return f'{self.source} ({self.description})'


class Identifier(models.Model):
    """
    A class that links Persons and identifiers in authentication sources
    """
    source = models.ForeignKey(IdSource,
                               on_delete = models.CASCADE,
                               db_index = True,
                               editable = False,
                               verbose_name = _('Identification source'))
    person = models.ForeignKey(Person,
                               on_delete = models.CASCADE,
                               db_index = True,
                               editable = False,
                               related_name = 'identifiers',
                               related_query_name = 'person_identifiers',
                               verbose_name = _('Person'))
    value = models.CharField(max_length = 128,
                             db_index = True,
                             editable = False,
                             verbose_name = _('Identifier value hash'))

    # Control data
    createdOn = models.DateTimeField(verbose_name = _('Created on'),
                                     auto_now_add = True,
                                     db_index = True,
                                     editable = False)
    modifiedOn = models.DateTimeField(verbose_name = _('Modified on'),
                                      auto_now = True,
                                      db_index = True,
                                      editable = False)

    class Meta:
        verbose_name = _('Identifier')
        verbose_name_plural = _('Identifiers')
        index_together = ['source', 'person', 'value']
        ordering = ['person', 'source', 'value']
        constraints = [
            models.UniqueConstraint(fields=['person', 'source', 'value'],
                                    name='one_value_per_attribute_per_person'),
        ]


class HEI(models.Model):
    """
    A class for describing a Higher Education Institution
    These will be the root for administrators and students
    """

    MONTHS = [
                (1,_('January')),
                (2,_('February')),
                (3,_('March')),
                (4,_('April')),
                (5,pgettext('month name', 'May')),
                (6,_('June')),
                (7,_('July')),
                (8,_('August')),
                (9,_('September')),
                (10,_('October')),
                (11,_('November')),
                (12,_('December'))
             ]

    name = models.CharField(max_length = 100,
                            db_index = True,
                            verbose_name = _('Institution name'))
    termstart = models.SmallIntegerField(
                           choices = MONTHS,
                           verbose_name = _('Term start month'),
                           help_text = _(
                'Month the term starts on, for expiration date calculations.'))
    url = models.URLField(max_length = 256,
                           db_index = True,
                           blank = True,
                           null = True,
                           verbose_name = _('Institution web site'))
    country = CountryField(db_index = True, verbose_name = _('Country'))
    pic = models.CharField(max_length = 20,
                           db_index = True,
                           unique = True,
                           blank = True,
                           null = True,
                           verbose_name = _('PIC code'))
    euc = models.CharField(max_length = 50,
                           db_index = True,
                           unique = True,
                           blank = True,
                           null = True,
                           verbose_name = _('EUC code'))
    erc = models.CharField(max_length = 30,
                           db_index = True,
                           unique = True,
                           blank = True,
                           null = True,
                           verbose_name = _('Erasmus code'))
    oid = models.CharField(max_length = 10,
                           db_index = True,
                           unique = True,
                           blank = True,
                           null = True,
                           verbose_name = _('OID code'))
    sho = models.CharField(max_length = 100,
                           db_index = True,
                           unique = True,
                           blank = True,
                           null = True,
                           verbose_name = _('SCHAC Home Organization'),
                           help_text = _('Your Internet domain. For ESI'))
    # ESC router information
    productionKey = models.CharField(max_length = 100,
                                     blank = True,
                                     null = True,
                                     verbose_name = _('ESC production key'))
    sandboxKey = models.CharField(max_length = 100,
                                  blank = True,
                                  null = True,
                                  verbose_name = _('ESC sandbox key'))
    # Control attributes
    managedBy = models.ForeignKey(Person,
                                  on_delete = models.PROTECT,
                                  db_index = True,
                                  verbose_name = _('Responsible person'))
    createdOn = models.DateTimeField(verbose_name = _('Created on'),
                                     auto_now_add = True,
                                     db_index = True,
                                     editable = False)
    modifiedOn = models.DateTimeField(verbose_name = _('Modified on'),
                                      auto_now = True,
                                      db_index = True,
                                      editable = False)

    class Meta:
        verbose_name = _('Higher Education Institution')
        verbose_name_plural = _('Higher Education Institutions')
        ordering = ['country', 'name']


    def __str__(self):
        return '{0.name} - {0.sho} - {0.pic}'.format(self)

    def delete(self, *args, **kwargs):
        """
        Check that persons that entered the system via the deleted HEI
        get associated to other managing person if they have enrolments
        in other HEI 
        """
        for student in self.studentcards.all():
            card = student.person.cards.all().exclude(hei=self).first()
            if card is not None:
                # Person is enrolled in other HEI at least
                # Pass control to the manager of first HEI
                person = student.person
                person.managedBy = card.manager.person
                person.save()
        # Officers may be enrolled as students in other HEIs
        for officer in self.officers.all():
            card = officer.person.cards.all().exclude(hei=self).first()
            if card is not None:
                # Person is enrolled in other HEI at least
                # Pass control to the manager of first HEI
                person = officer.person
                person.managedBy = card.manager.person
                person.save()
        super(HEI, self).delete(*args, **kwargs)
            

    def generate_esc_code(self):
        """
        Returns an ESC for a student enroled in the HEI
        It is HEI specific, thus, we use a HEI object level method
        """
        # The machine ID is used by ESC in case there are more than one system
        # producing ESC cards for an instituion, usually it is just one
        machineId = get_setting('MACHINEID','001')
        uu = uuid.uuid1(node=int('{}{}'.format(machineId, self.pic), 10))
        return str(uu)[:-12]+'{0:>012}'.format(uu.node)

    def ESC_Router(self, operation, **kwargs):
        """
        Does and ESC Router operation GET, PUT, POST, DELETE
        Depending on the operation the expected keyword args are:
        esi: an European Student Identifier
        esc: an European Student Card number
        json: a JSON dictionary with information to store in the router

        Returns a requests result or a mock-up object for big errors
        """

        class Mockup():
            """Mockup class to resemble a requests response"""
            def __init__(self):
                self.status_code = 500
                self.url = 'Error'
                self.json = {}
                self.text = _('Fatal error calling ESC_Router()')
        
        # Is an accepted operation?
        r = Mockup()
        if operation not in ['GET', 'PUT', 'POST', 'DELETE']: return r
        # Expected keyword parameters
        esi = kwargs.get('esi', None)
        esc = kwargs.get('esc', None)
        json = kwargs.get('json', None)
        # Do we have any of the expected parameters
        r.text = '{}. {}'.format(r.text, _('No information to store'))
        if esi is None and esc is None and json is None: return r
        headers = {'Content-Type': 'application/json',
                   'key': self.productionKey }

        base_url = get_setting('ESCROUTER_BASE_URL', None)

        # If the system or the HEI is not yet in production, use the sandbox
        if not base_url or not self.productionKey:
            base_url = get_setting('ESCROUTER_SANDBOX_URL', None)
            if not base_url or not self.sandboxKey:
                # If the HEI is not connected to the ESC Router, do no harm
                if operation == 'GET': return None
                if operation in ['PUT', 'POST']: r.status_code = 201
                if operation == 'DELETE': r.status_code = 204
                r.url = 'Success'
                r.text = 'OK'
                return r
            headers['key'] = self.sandboxKey

        # GET 
        if operation == 'GET':
            if esi is None: return None
            r = requests.get(
                    parse.urljoin(base_url, esi),
                    headers = headers,
                    timeout = get_setting('ESCROUTER_TIME_OUT',1)
                )
            if r.status_code == 200: return r.json()

        if operation == 'PUT':
            if json is None: return None
            esi =  json.get('europeanStudentCardNumber', None)
            if esi is None: return r
            r = requests.put(
                    parse.urljoin(base_url, esi),
                    headers = headers,
                    json = json,
                    timeout = get_setting('ESCROUTER_TIME_OUT',1)
                )
            return r

        if operation == 'POST':
            if json is None and esc is None: return None
            # Are we adding a card?
            if json is None and esc is not None and esi is not None:
                base_url = parse.urljoin(base_url, '{}{}'.format(esi, '/cards'))
                json = {'europeanStudentCardNumber': esc,
                        'cardType': 1}
            r = requests.post(base_url, headers = headers, json = json,
                    timeout = get_setting('ESCROUTER_TIME_OUT',1))
            return r

        if operation == 'DELETE':
            if esi is None and esc is None: return r
            if esc is not None and esi is not None:
                # Delete a card
                base_url = parse.urljoin(base_url,
                                         '{}{}'.format(esi, '/cards/', esc))
            if esi is not None:
                # Delete a student
                base_url = parse.urljoin(base_url, esi)
            r = requests.post(base_url, headers = headers,
                    timeout = get_setting('ESCROUTER_TIME_OUT',1))
            return r

        # If we reach here, better return None
        return None

    def pdf_cards(self):
        if not os.path.exists('/tmp/qr-cards'):
            os.mkdir('/tmp/qr-cards')

        # Information position from card top left corner
        location = {'name': (5, 30), 'esi': (5, 40),
                    'qr': (59, 20), 'esc': (5, 45)}
        start = {'x': 12, 'y': 10}
        gap = {'x': 10, 'y': 2}
        size = {'x': 85, 'y': 55}


        pdf = FPDF('P','mm','A4')
        pdf.add_font('DejaVu','',
                     '/usr/share/fonts/dejavu/DejaVuSans.ttf',uni=True)
        pdf.add_font('DejaVu','B',
                     '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf',uni=True)

        count = 0
        for card in self.studentcards.all():
            qr = f'/tmp/qr-cards/{card.esc}.png'
            if not os.path.exists(qr):
                open(qr,'wb').write(card.myESCQR(b64=False).read())
            
            if count % 10 == 0: pdf.add_page()
            hpos = (count % 2)
            vpos = int((count % 10)/2) if hpos == 0 else vpos
            x = start['x']+(size['x']*(hpos))+(gap['x']*hpos)
            y = start['y']+(size['y']*(vpos))+(gap['y']*vpos) if hpos == 0 else y

            pdf.line(x, y, x+size['x'], y)
            pdf.line(x+size['x'], y, x+size['x'], y+size['y'])
            pdf.line(x+size['x'], y+size['y'], x, y+size['y'])
            pdf.line(x, y+size['y'], x, y)

            pdf.set_xy(x + location['name'][0], y + location['name'][1])
            fullname = f'{card.student.first_name} {card.student.last_name}'
            pdf.set_font('DejaVu', 'B', 11)
            if len(fullname) > 24:
                pdf.set_font('DejaVu', 'B', 10)
            if len(fullname) > 27:
                pdf.set_font('DejaVu', 'B', 9)
            if len(fullname) > 30:
                pdf.set_font('DejaVu', 'B', 8)
            pdf.cell(0,10,fullname)
            pdf.set_xy(x + location['esi'][0], y + location['esi'][1])
            pdf.set_font('DejaVu','',9)
            pdf.cell(0,10,f'{card.esi}')
            pdf.set_xy(x + location['esc'][0], y + location['esc'][1])
            pdf.set_font('DejaVu','',9)
            pdf.cell(0,10,f'{card.esc}')
            pdf.image(qr, x + location['qr'][0], y + location['qr'][1], 25, 25)

            count = count + 1

        return pdf.output(name="" ,dest="S").encode('latin1')
        return pdf

class Officer(models.Model):
    """A class for linking persons to the institutions they manage"""

    person = models.ForeignKey(Person,
                               on_delete = models.CASCADE,
                               db_index = True, 
                               related_name = 'manages',
                               related_query_name = 'manage',
                               verbose_name = _('Person that manages a HEI'))
    hei = models.ForeignKey(HEI,
                            on_delete = models.CASCADE,
                            db_index = True, 
                            related_name = 'officers',
                            related_query_name = 'officer',
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
        ordering = ['hei', 'person']
        constraints = [
            models.UniqueConstraint(fields=['person', 'hei'],
                                    name='manager_unique')
        ]

    def __str__(self):
        return '{0.person} => {0.hei}'.format(self)

    def delete(self, *args, **kwargs):
        """
        Check that officer dependencies have been passed onto other officer
        """
        # The replacement will be the first officer from the same HEI
        replacements = Officer.objects.filter(hei = self.hei)
        replacements.exclude(person = self.person)
        # Officer cannot be deleted, here is no replacement
        if len(replacements) == 0: return False
        # Pass HEI to the first replacement in line
        self.hei.managedBy = replacement[0].person
        # Pass all cards to the first replacement in line
        self.cards.all().update(manager = replacements[0])
        # Pass objects related to the person that is the deleted officer
        # but only those that belong to the same HEI as the Officer
        #self.person.persons.all().update(managedBy = replacements[0].person)
        #self.person.manages.all().update(managedBy = replacements[0].person)
        # Remove staff status if the person does not manage any HEI

        super(Officer, self).delete(*args, **kwargs)



class StudentCard(models.Model):
    """
    A class for describing student cards.
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
                            db_index = True, 
                            related_name = 'studentcards',
                            related_query_name = 'studentcard',
                            verbose_name = _("Person's HEI"))
    esc = models.CharField(max_length = 300,
                           db_index = True, 
                           editable = False,
                           unique = True,
                           verbose_name = _('European Student Card number'))
    esi = models.CharField(max_length = 300,
                           db_index = True, 
                           unique = True,
                           verbose_name = _('Student specific part of ESI'),
                           help_text = 'ESI: European Student Identifier')

    # Control information
    manager = models.ForeignKey(Officer,
                                on_delete = models.PROTECT,
                                related_name = 'cards',
                                related_query_name = 'card',
                                verbose_name = _('Responsible officer'))
    createdOn = models.DateTimeField(_('Created on'),
                                     auto_now_add = True,
                                     db_index = True,
                                     editable = False)
    modifiedOn = models.DateTimeField(_('Modified on'),
                                      auto_now = True,
                                      db_index = True,
                                      editable = False)
    registeredOn = models.DateTimeField(verbose_name = _('ESC registered on'),
                                        null = True,
                                        db_index = True,
                                        editable = False)


    class Meta:
        verbose_name = _('Card')
        verbose_name_plural = _('Cards')
        index_together = ['esi', 'hei', 'student']
        ordering = ['hei', 'student']
        constraints = [
            models.UniqueConstraint(fields=['esi', 'hei', 'student'],
                                    name='card_unique')
        ]

    def __str__(self):
        return '{0.student} - {0.esc} - {1}'.format(self, self.myESI())

    def save(self, *args, **kwargs):
        """
        Check some data and do whatever maybe needed.
        """
        # Do we have an ESC number?
        if self.esc is None or self.esc == '':
            # Generate the ESC
            self.esc = self.hei.generate_esc_code()
        # Does the card exist in the ESC router? It does if it was registered
        if not self.is_registered and self.student.has_accepted:
            # If the person has consented and card is not in the ESCR, save it
            self.save_in_ESCR()
        super(StudentCard, self).save(*args, **kwargs)

    @property
    def is_registered(self):
        return self.registeredOn is not None

    def delete(self, *args, **kwargs):
        """
        Clean up in the ESC Router before deleting local information.
        """
        if self.is_registered:
            # Only call the ESC Router if the card has been registered
            if not self.delete_card():
                # ESC deletion failed, we can't delete the card
                return
            if self.delete_student():
                # ESC deletion failed, we can't delete the card
                return
            self.registered = None
        super(StudentCard, self).delete(*args, **kwargs)
            
    def myESCURL(self):
        """
        Return the ESC verification URL for generating a QR code.
        """
        base_url = get_setting('ESCROUTER_VERIFY_URL', None)
        if base_url is None: return ''
        return f'{base_url}/{self.esc}'

    def myESCQR(self, b64=True):
        """
        Return the ESC verification QR code.
        The format is base64 ASCII encoded, so it can be inserted as
        an HTML image source.
        If b64 is False, the byte stream is returned raw.
        """
        qr = io.BytesIO()
        qrcode.make(self.myESCURL()).save(qr)
        qr.seek(0)
        if b64:
            qr = base64.b64encode(qr.read()).decode('ascii')
        return qr

    def myESI(self, myacid = False):
        """
        Return the European Student Identifier (ESI)
        in ESC format if myacid is False (default)
            CC-PIC-identifier
        in MyAcademicId (URN) format if myacid is True
            urn:schac:PersonalUniqueCode:scope:identifier
        """
        code = f'urn:schac:PersonalUniqueCode:int:esi:{self.hei.sho}:{self.esi}'
        if myacid:
            return code
        return f'{self.hei.country.code}-{self.hei.pic}-{self.esi}'

    def expires(self):
        """
        Student status expiration date.
        ISO 8601 Date Time Format: yyyy-mm-dd:59:59.000X.
        If current month is before term start, year is current year,
        otherwise it is set to the next calendar year.
        Month is the term starting month.
        """
        now = timezone.now()

        year = now.year
        if now.month > self.hei.termstart: year += 1

        day = calendar.monthrange(year, self.hei.termstart)[1]

        expiration = timezone.datetime(year, self.hei.termstart, day,
                                       23, 59, 00)
        return expiration.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    def get_remote(self):
        """
        Returns a dictionary with the information stored in the
        European Student Card Router for a given ESI.
        None if it doesn't exist.
        Ex:
           {
               u'cards': [
                   {
                       u'cardType': 1,
                        u'europeanStudentCardNumber': 
                                u'b881984a-0b88-11e9-98a4-0000773406c7',
                    }
                ],
                u'emailAddress': u'0617102195@uma.es',
                u'europeanStudentIdentifier': u'ES-999898311-0617102195',
                u'expiryDate': u'2019-12-31T23:59:59.000Z',
                u'picInstitutionCode': 999898311,
            }
        """
        return self.hei.ESC_Router('GET', esi = self.myESI())


    @property
    def card_exists(self):
        """
        Returns True if the card exists in the ESC Router.
        False if it does not.
        """
        return bool(self.get_remote())

    @property
    def cards(self):
        """
        Returns a list of cards from the ESC router
        that have the same ESI as the current one.
        """
        attributes = self.get_remote()
        if attributes and attributes.get("cards", list()):
            return [x.get('europeanStudentCardNumber', None)
                    for x in attributes['cards']]
        return list()

    def save_in_ESCR(self, debug=False):
        """
        Insert or update the card in the European Student Card Router,
        Returns True if everything went well.
        """
        data = {'europeanStudentIdentifier': self.myESI(),
                'picInstitutionCode': self.hei.pic,
                'emailAddress': self.student.email,
                'expiryDate': self.expires()
               }

        operation = 'POST'
        if self.is_registered: operation = 'PUT'
        r = self.hei.ESC_Router(operation, json = data)
        if r.status_code != 201:
            if debug:
                return r.status_code, r.url, 'Add card response', r.text
            return False

        if self.esc not in self.cards:
            # Add card
            r = self.hei.ESC_Router('POST', esi = self.myESI(), esc = self.esc)
            if r.status_code != 201:
                if debug:
                    return r.status_code, r.url, 'Add card response', r.text
                return False

        if operation == 'POST': 
            self.registeredOn = timezone.now()

        return True

    def delete_card(self, student=False):
        """
        Removes the information about the card from the ESC Router.
        If there are no cards left and student is True, removes the student.
        """
        result = True
        cards = self.cards
        if self.esc in cards:
            # Delete card
            r = self.hei.ESC_Router('DELETE',
                                    esi = self.myESI(), esc = self.esc)
            if r.status_code != 204: return False
            cards.remove(self.esc)
        if student and len(cards) == 0:  # Explicit is better than implict
            # No cards left for the ESI
            result = self.delete_student()
        return result

    def delete_student(self):
        """
        Removes the information about the student from the ESC Router.
        Only students with no cards can be removed.
        """
        if len(self.cards) == 0:
            # No cards left for the ESI
            r = self.hei.ESC_Router('DELETE', esi = self.myESI())
            return r.status_code == 204

        return False

# We import the signals so they are bound to the objects
from . import signals

