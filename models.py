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
from django_countries.fields import CountryField
from django.contrib.auth.models import AbstractUser
AbstractUser._meta.get_field('email')._unique = True

from urllib import parse
import uuid
import requests

# Create your models here.

class HEI(models.Model):
    """A class for describing a High Education Institution
    These will be the root for administrators and students
    """

    MONTHS = [
                (1,_('January')),
                (2,_('February')),
                (3,_('March')),
                (4,_('April')),
                (5,_('May')),
                (6,_('June')),
                (7,_('July')),
                (8,_('August')),
                (9,_('September')),
                (11,_('October')),
                (11,_('November')),
                (12,_('December'))
             ]

    name = models.CharField(max_length = 100,
                            db_index = True,
                            verbose_name = _('Institution name'))
    termstart = models.SmallIntegerField(
                           choices = MONTHS,
                           verbose_name = _('Term start month'),
                           help_text = _('Month the term starts on.'
                                         ' Used for expiry date calculations.'))
    url = models.URLField(max_length = 256,
                           db_index = True,
                           blank = True,
                           null = True,
                           verbose_name = _('Institution web site'))
    country = CountryField(db_index = True, verbose_name = _('Country'))
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

    class Meta:
        verbose_name = _('Higher Education Institution')
        verbose_name_plural = _('Higher Education Institutions')


    def __str__(self):
        return '{0.name} - {0.sho} - {0.pic}'.format(self)

    def generate_esc_code(self):
        """
        Returns an ESC for a student enroled in the HEI
        It is HEI specific, thus, we use a HEI object level method
        """
        import uuid
        # The machine ID is used by ESC in case there are more than system
        # producing ESC cards for an instituion, usually it is just one
        machineId = settings.__dict__.get('MACHINEID','001')
        return str(uuid.uuid1(node=int('{}{}'.format(machineId,
                                                     self.pic), 10)))

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

        base_url = settings.__dict__.get('ESCROUTER_BASE_URL', None)

        # If the system or the HEI is not yet in production, use the sandbox
        if not base_url or not self.productionKey:
            base_url = settings.__dict__.get('ESCROUTER_SANDBOX_URL', None)
            if not base_url or not self.sandboxKey:
                return None
            headers['key'] = self.sandboxKey

        # GET 
        if operation == 'GET':
            esi = kwargs.get('esi', None)
            if esi is None: return None
            r = requests.get(
                    parse.urljoin(base_url, esi),
                    headers = headers,
                    timeout = settings.__dict__.get(ESCROUTER_TIME_OUT,1)
                )
            if r.status_code == 200: return r.json()

            if debug: return 'Error response', r.text

        if operation == 'PUT':
            if json is None: return None
            esi =  json.get('europeanStudentCardNumber', None)
            if esi is None: return r
            r = requests.put(
                    parse.urljoin(base_url, esi),
                    headers = headers,
                    json = json,
                    timeout = settings.__dict__.get(ESCROUTER_TIME_OUT,1)
                )
            return r

        if operation == 'POST':
            if json is None and esc is None: return None
            # Are we adding a card?
            if json is None and esc is not None and esi is not None:
                base_url = parse.urljoin(base_url, '{}{}'.format(esi, '/cards'))
                json = {'europeanStudentCardNumber': esc,
                        'cardType': 1},
            r = requests.post(base_url, headers = headers, json = json,
                    timeout = settings.__dict__.get(ESCROUTER_TIME_OUT,1))
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
                    timeout = settings.__dict__.get(ESCROUTER_TIME_OUT,1))
            return r

        # If we reach here, better return None
        return None


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
                                  verbose_name = _('Responsible person'))
    createdOn = models.DateTimeField(verbose_name = _('Created on'),
                                     auto_now_add = True,
                                     db_index = True,
                                     editable = False)
    modifiedOn = models.DateTimeField(verbose_name = _('Modified on'),
                                      auto_now = True,
                                      db_index = True,
                                      editable = False)
    acceptedOn = models.DateTimeField(verbose_name = _('Accepted on'),
                                      null = True,
                                      blank = True,
                                      db_index = True,
                                      editable = False)

    # It is possible to override the defaults in settings.py
    USERNAME_FIELD = settings.__dict__.get('PERSON_USERNAME_FIELD', 'email')
    REQUIRED_FIELDS = settings.__dict__.get('PERSON_REQUIRED_FIELDS', [])

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

    def has_accepted(self):
        return self.acceptedOn is not None


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
    registeredOn = models.DateTimeField(verbose_name = _('Registered on'),
                                        null = True,
                                        blank = True,
                                        db_index = True,
                                        editable = False)


    class Meta:
        verbose_name = _('Card')
        verbose_name_plural = _('Cards')
        index_together = ['esi', 'hei', 'student']
        constraints = [
            models.UniqueConstraint(fields=['esi', 'hei', 'student'],
                                    name='card_unique')
        ]

    def __str__(self):
        return '{0.student} - {0.esc} - {1}'.format(self, self.myESI())

    def save(self, *args, **kwargs):
        """Check some data and generate what maybe needed"""
        if self.esc is None or self.esc == '':
            # Generate the ESC
            self.esc = self.hei.generate_esc_code()
            super(StudentCard, self).save(*args, **kwargs)

    def is_registered(self):
        return self.registeredOn is not None

    def myESI(self, myacid = False):
        """
        Return the European Student Identifier (ESI)
        in ESC format if myacid is False (default)
            CC-PIC-identifier
        in MyAcademicId (URN) format if myacid is True
            urn:schac:PersonalUniqueCode:scope:identifier
        """
        code = 'urn:schac:PersonalUniqueCode:int:{}:{}'.format(self.hei.sho,
                                                               self.esi)
        if myacid:
            return code
        return '{}-{}-{}'.format(self.hei.country.code, self.hei.pic, self.esi)

    def expires(self):
        """
        Student status expiry date.
        ISO 8601 Date Time Format: yyyy-mm-dd:59:59.000X.
        If current month is before term start, year is current year,
        otherwise it is set to the next calendar year.
        Month is the term starting month.
        """
        now = datetime.date.now()

        year = now.year
        if now.month > self.hei.termstart: year += 1

        day = calendar.monthrange(year, self.hei.termstart)[1]

        expiration = datetime.datetime(year, self.hei.termstart, day,
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
        If debug is True, it returns more information.
        """
        return self.hei.ESC_Router('GET', esi = self.myESI())


    def card_exists(self):
        """
        Returns True if the card exists in the ESC Router.
        False if it does not.
        """
        return bool(self.get_remote())

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

    def save_in_ESCR(self, debug = False):
        """
        Insert or update the card in the European Student Card Router,
        Returns True if everything went well.
        """
        data = {'europeanStudentIdentifier': self.myESI(),
                'picInstitutionCode': self.PIC_INSTITUCION_CODE,
                'emailAddress': self.email_address,
                'expiryDate': expiry_date
               }

        operation = 'POST'
        if self.card_exists(): operation = 'PUT'
        r = self.hei.ESC_Router(operation, json = data)
        if r.status_code != 201:
            if debug:
                return r.status_code, r.url, 'Insert student error', r.text
            return False

        if self.esc not in self.cards():
            # Add card
            r = self.hei.ESC_Router('POST', esi = self.myESI(), esc = self.esc)
            if r.status_code != 201:
                if debug:
                    return r.status_code, r.url, 'Add card response', r.text
                return False

        if operation == 'POST': 
            self.registeredOn = datetime.datetime.now()
            self.save()

        if debug:
            return r.status_code, r.url, 'Last response', r.text
        return True

    def delete_card(self):
        """
        Removes the information about the card from the ESC Router.
        If there are no cards left, removes the student.
        """
        result = True
        if self.esc in self.cards():
            # Delete card
            r = self.hei.ESC_Router('DELETE',
                                    esi = self.myESI(), esc = self.esc)
            if r.status_code != 204:
                if debug:
                    return r.status_code, r.url, 'Delete card error', r.text
                return False
        if len(self.cards()) == 0:
            # No cards left for the ESI
            result = self.delete_student()
        return result

    def delete_student(self):
        """
        Removes the information about the student from the ESC Router.
        Only students with no cards can be removed.
        """
        result = False
        if len(self.cards()) == 0:
            # No cards left for the ESI
            r = self.hei.ESC_Router('DELETE', esi = self.myESI())
            if debug:
                return r.status_code, r.url, 'Delete student response', r.text
            return r.status_code == 204

        return result


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

    def __str__(self):
        return '{0.person} => {0.hei}'.format(self)

