# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$

from django.contrib import admin
from django.contrib import messages
from django.template.response import TemplateResponse
from django.urls import path
from django.db.models import Q
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ngettext
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.conf import settings
from django import forms

from .utils import get_setting

import codecs
import csv
import io

# Register your models here.
from .models import HEI, Person, Officer, StudentCard, IdSource, Identifier
from .forms import cardLoadForm, heiLoadForm, officerLoadForm

###########################
# Filters
###########################
class HasAcceptedListFilter(admin.SimpleListFilter):
    title = _('Has accepted')
    parameter_name = 'hasaccepted'

    def lookups(self, request, mdl):
        return (('True', _('Yes')), ('False',_('No')))

    def queryset(self, request, queryset):
        if self.value():
            # We need to reverse the meaning as we are looking for nulls
            # so hasaccepted is true when acceptedOn is NOT null
            what = self.value() == 'False'
            return queryset.filter(acceptedOn__isnull=what)
        else:
            return queryset

class IsInvitedListFilter(admin.SimpleListFilter):
    title = _('Is Invited')
    parameter_name = 'isinvited'

    def lookups(self, request, mdl):
        return (('True', _('Yes')), ('False',_('No')))

    def queryset(self, request, queryset):
        if self.value():
            # We need to reverse the meaning as we are looking for nulls
            # so isinvited is true when invitedOn is NOT null
            what = self.value() == 'False'
            return queryset.filter(invitedOn__isnull=what)
        else:
            return queryset

class CountryListFilter(admin.SimpleListFilter):
    title = 'Country'
    parameter_name = 'country'

    def lookups(self, request, mdl):
        # We filter countries for objects managed by the current user
        objects = mdl.model.objects.filter(managedBy=request.user)
        countries = set([t.country for t in objects])
        return [(country, country) for country in countries]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(country=self.value())
        else:
            return queryset


###########################
# Actions
###########################
def send_invites(modeladmin, request, queryset):
    """
    Resend invitations to the selected persons
    """
    for person in queryset:
        if person.is_superuser:
            template = 'esiidm/super_invite.txt'
            hei = None
        elif person.is_officer:
            template = 'esiidm/officer_invite.txt'
            # Persons consent when they are inserted for the first HEI
            hei = person.myHEI
        else:
            # Person is a student
            template = 'esiidm/student_invite.txt'
            # Persons consent when they are inserted for the first HEI
            hei = person.myHEI
        host = get_setting('MAIL_ORIGIN_DOMAIN',
                           request.get_host().split(':')[0])
        result = person.invite(person.managedBy, hei=hei,
                               host=host, template=template)
        if not result:
            modeladmin.message_user(
                            request,
                            _('Could not send message to {0}').format(person.email),
                            messages.WARNING)
send_invites.short_description = _('Send invite to selected persons')


###########################
# Model admins
###########################
class IdentifierInline(admin.TabularInline):
    model = Identifier
    hidden_fields = ('id')
    readonly_fields = ('source', 'value', 'createdOn')
    extra = 0

    def has_view_permission(self, request, obj=None):
        if not super(IdentifierInline, self).has_view_permission(request, obj):
            return False
        if obj is None : return True
        # Not even superusers should view Identifiers for
        # Persons they do not manage
        if obj is not None and request.user.id == obj.managedBy.id:
            return True
        # Persons with admin privileges can view their data
        if obj is not None and request.user.id == obj.id:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        # Nobody may change identifier data, it has to happen from an invite
        return False


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_filter = [ HasAcceptedListFilter, IsInvitedListFilter ]
    search_fields = ['email', 'identifier', 'last_name']
    list_display_links = ['email', 'identifier', 'last_name']
    list_display = ['last_name', 'first_name', 'email', 'identifier',
                    'has_accepted', 'is_officer', 'is_superuser']
    readonly_fields = ['acceptedOn', 'invitedOn', 'last_login', 'date_joined']
    inlines = [ IdentifierInline ]
    actions = [ send_invites ]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj=None, **kwargs)
        disabled_fields = set()
        if not request.user.is_superuser:
            disabled_fields |= {'is_superuser',
                                'user_permissions', 'managedBy'}
        if (not request.user.is_superuser
            and obj is not None
            and obj == request.user
           ):
            disabled_fields |= {'is_staff', 'is_superuser',
                                'groups', 'user_permissions'}
        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True
        return form

    def has_module_permission(self, request, obj=None):
        if request.user.is_anonymous: return False
        if request.user.is_superuser or request.user.is_officer: return True
        if super(PersonAdmin, self).has_module_permission(request, obj):
            return True
        return False

    def has_view_permission(self, request, obj=None):
        if obj is None : return True
        # Not even superusers should view Persons they do not manage
        if obj is not None and request.user.id == obj.managedBy.id:
            return True
        # Persons with admin privileges can view their data
        if obj is not None and request.user.id == obj.id:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if obj is None : return True
        # Not even superusers should alter Persons they do not manage
        if obj is not None and request.user.id == obj.managedBy.id:
            return True
        return False

    def get_changeform_initial_data(self, request):
        return {'managedBy': request.user}

    def get_listdisplay(self, request, obj=None):
        # Is the user a superuser or an officer for several HEIs
        if request.user.is_superuser or (request.user.is_officer and
                                         request.user.HEIs.count() > 1):
            if 'myHEI' not in self.list_display:
                self.list_display.append('myHEI')
        return self.list_display

    def get_queryset(self, request):
        return Person.objects.filter(managedBy=request.user)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.managedBy = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "managedBy":
            kwargs["queryset"] = Person.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    #def get_readonly_fields(self, request, obj=None):
    #    readonly_fields = []
    #    if not request.user.is_superuser and request.user.is_officer:
    #        readonly_fields = []
    #    return readonly_fields

    def get_fieldsets(self, request, obj=None):
        # Adapt the field sets depending on who's managing the person
        # (_(''), {'fields': []}),
        fieldsets = [(None, {'fields': [('first_name','last_name'),
                                        ('email','identifier')]}),]
        if obj is None:
            if 'password' not in fieldsets[0][1]['fields']:
                fieldsets[0][1]['fields'].append('password')
        if request.user.is_staff or request.user.is_superuser:
            if 'managedBy' not in fieldsets[0][1]['fields']:
                fieldsets[0][1]['fields'].append('managedBy')
        if request.user.is_superuser and len(fieldsets) == 1:
            fieldsets.append((_('Access control'), {'classes': ('collapse',),
                                                    'fields': [('is_active',
                                                               'is_staff',
                                                               'is_superuser')
                                                              ]}))
            fieldsets.append((_('Permissions'), {'classes': ('collapse',),
                                                 'fields': ['user_permissions',
                                                            'groups']}))
            fieldsets.append((_('Administrivia'), {'classes': ('collapse',),
                                                   'fields': [('invitedOn',
                                                               'acceptedOn',
                                                               'last_login',
                                                               'date_joined')
                                                             ]}))
        return fieldsets


@admin.register(HEI)
class HEIAdmin(admin.ModelAdmin):
    search_fields = ['name', 'pic', 'euc', 'oid', 'sho']
    list_display = ['name', 'pic', 'sho', 'oid', 'url', 'erc']
    list_display_links = ['name', 'pic', 'oid', 'sho']

    def has_module_permission(self, request, obj=None):
        if request.user.is_anonymous: return False
        if request.user.is_superuser or request.user.is_officer: return True
        if super(HEIAdmin, self).has_module_permission(request, obj):
            return True
        return False

    def has_view_permission(self, request, obj=None):
        # Only superusers or the manager for the HEI can view a HEI
        if obj is None : return True
        if obj is not None and (request.user.id == obj.managedBy.id
                                or request.user.is_superuser):
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if obj is None : return True
        # Only superusers or the manager for the HEI can chage a HEI
        if obj is not None and (request.user.id == obj.managedBy.id
                                or request.user.is_superuser):
            return True
        if obj is not None and (obj in request.user.HEIs):
            return True
        return False

    def get_exclude(self, request, obj=None):
        # Allow the Superusers to "get rid" of HEIs by changing the manager
        if request.user.is_superuser:
            return []
        return ['managedBy',]
        
    def get_list_display(self, request, obj=None):
        if request.user.is_superuser: 
            if 'country' not in self.list_display:
                self.list_display.insert(0,'country')
            if 'managedBy' not in self.list_display:
                self.list_display.insert(2,'managedBy')
        return self.list_display

    def get_list_filter(self, request, obj=None):
        if request.user.is_superuser: return [CountryListFilter]
        return []

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "managedBy":
            kwargs["queryset"] = Person.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        if request.user.is_superuser: return HEI.objects.all()
        if request.user.is_officer: return request.user.HEIs
        return HEI.objects.filter(managedBy=request.user)

    def save_model(self, request, obj, form, change):
        if not change and obj.managedBy is None:
            obj.managedBy = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = []
        if not request.user.is_superuser and request.user.is_officer:
            readonly_fields = ['name', 'country', 'oid',
                               'pic', 'sho', 'euc', 'erc']
        return readonly_fields

    def get_fieldsets(self, request, obj=None):
        # Adapt the field sets depending on who's managing the HEI
        # (_(''), {'fields': []}),
        fieldsets = [(None, {'fields': [('name', 'country', 'url'),
                                        'termstart',]}),
                     (_('Erasmus'), {'fields': [('oid', 'euc'),
                                                ('erc', 'sho', 'pic')]}),
                     (_('European Student Card'), {'fields': ['productionKey',
                                                              'sandboxKey']})]
        if request.user.is_superuser and len(fieldsets) == 3:
            fieldsets.append((_('Access control'),
                             {'fields': [('managedBy',)]}))
        return fieldsets

    def get_urls(self):
        urls = super().get_urls()
        urls.insert(0, path('hei_load/',
                    self.admin_site.admin_view(self.load_heis)))
        return urls

    def load_heis(self, request):
        """
        A view for loading HEIs.
        Only superusers can load HEIs.
        HEIs are uploaded in CSV format with a minimum set of fields:
            - name : HEI name
            - country : HEI country ISO two letter code
            - sho : SCHAC Home Organization (HEI Internet domain)
            - manager : email address for the main HEI officer
        Optional fields:
            - first_name : Main officer's given name
            - last_name : Main officer's family name
            - pic : HEI PIC code
            - euc : HEI EUC code
            - oid : HEI OID code
            - erc : HEI Erasmus code
            - url : HEI main web page
            - termstart : month when term starts (1 through 12)
        At least one of pic, euc, oid or erc MUST (RFC 2119) be present
        """
    
        user = request.user
        if not user.is_superuser: 
            return HttpResponseForbidden(_('Access not permitted'))
        errors = []
        if request.method == 'POST':
            # Process the form
            form = heiLoadForm(request.POST, request.FILES)
            # The "C" in CSV means "Comma",
            # although sometimes Excel thinks it means "semicolon"
            delimiter = request.POST.get('delimiter', ',')
            data = request.FILES['data']
            data.seek(0)
            lines = csv.DictReader(io.StringIO(data.read().decode('utf-8-sig')),
                                   delimiter=delimiter)
            # There must be at least one line and it must contain the required fields
            total = 1
            inserted = 0
            new_persons = []
            # Let's load the data
            for line in lines:
                total += 1
                errors_in_line = False
                for field in ['name', 'country', 'manager', 'sho']:
                    if line.get(field, '').strip() == '':
                        errors_in_line = True
                        errors.append(_('Field {0} missing on line {1}').format(field, total))
                if errors_in_line: continue
                identification = False
                for field in ['pic', 'euc', 'erc', 'oid']:
                    if not line.get(field, '').strip() == '':
                        identification = True
                # Can we identify de HEI?
                #if not identification:
                #    errors.append(_('None of pic, euc, erc or oid present on line {0}').format(total))
                #    continue
                manager_mail = line.get('manager', '').strip()
                manager = Person.objects.filter(email=manager_mail).first()
                new = False
                # Do we have a main manager or can we add one?
                if manager is None:
                    first_name = line.get('first_name', '').strip()
                    last_name = line.get('last_name', '').strip()
                    if first_name == '' or last_name == '':
                        e = _('Person {0} in line {1} does not exist. '
                              'Not enough information to add a person.')
                        errors.append(e.format(manager_mail, total))
                        continue
                    # Create the person
                    manager = Person(email=manager_mail)
                    new = True
                    manager.first_name = first_name
                    manager.last_name = last_name
                    manager.managedBy = request.user
                    manager.is_staff = True
                    manager.save()
    
                # We are good, check if the HEI exists
                # As SHO is a required field and it MUST be unique, it's easy
                hei = HEI.objects.filter(sho=line['sho'].strip()).first()
                if hei is not None:
                    e = _('{0} already exists in line {1}').format(hei, total)
                    errors.append(e)
                    continue
                hei = HEI()
                hei.name = line['name'].strip()
                hei.country = line['country'].strip()
                hei.sho = line['sho'].strip()
                hei.managedBy = manager
                hei.pic = line.get('pic', '').strip()
                hei.euc = line.get('euc', '').strip()
                hei.erc = line.get('erc', '').strip()
                hei.oid = line.get('oid', '').strip()
                hei.url = line.get('url', '').strip()
                hei.termstart = line.get('termstart',
                                         get_setting('TERM_START',9)).strip()
                try:
                    hei.save()
                    inserted += 1
                    # We have to promote the person to officer level for HEI
                    # It should not exist, as we are creating the HEI
                    officer, n = Officer.objects.get_or_create(hei=hei,
                                                               person=manager,
                                                               manager=user)
                    # Add manager to the list of invites
                    if new: new_persons.append((manager, hei))
                    # and grant access to the admin pages
                    if not manager.is_staff:
                        manager.is_staff = True
                        manager.save()
                except Exception as ex:
                    es = _('Problem with {0} in line {1}: {2}')
                    e = es.format(hei, total, ex)
                    errors.append(e)
                    continue
            # Data processed, how did it go...
            # At least one HEI inserted
            if not inserted == 0:
                self.message_user(request,
                                  ngettext('{0} HEI loaded',
                                           '{0} HEIs loaded',
                                           inserted).format(inserted),
                                  messages.SUCCESS)
            # Person objects created
            newpersons = len(new_persons)
            if not newpersons == 0:
                self.message_user(request,
                                  ngettext('{0} person created',
                                           '{0} persons created',
                                           newpersons).format(newpersons),
                                  messages.SUCCESS)
            # We can send the invites to those that have just been added
            # to the system, asking for consent
            for person in new_persons:
                result = person[0].invite(request.user,
                                          host=request.get_host(),
                                          hei=person[1],
                                          template='esiidm/officer_invite.txt')
                if not result:
                    errors.append(_('Message to {0} not sent').format(person[0].email))
            # All went well, no errors
            if len(errors) == 0:
                return redirect('..')
            for e in errors: 
                self.message_user(request, e, messages.WARNING)
        # Render the form
        if len(errors) == 0:
            # Get a fresh form
            form = heiLoadForm()
        context = dict(self.admin_site.each_context(request), form = form)
        return TemplateResponse(request, 'esiidm/load_heis.html', context)


@admin.register(Officer)
class OfficerAdmin(admin.ModelAdmin):
    #list_filter = ['hei__name', 'hei__sho', 'hei__pic', 'hei__oid']
    list_filter_select = True
    select_related = True
    search_fields = ['person__email',
                     'hei__pic',
                     'hei__euc',
                     'hei__oid',
                     'hei__sho']
    list_display = ['person','hei',]
    list_display_links = ['person',]
    #fieldsets = [(None, {'fields': [('person', 'hei'), 'manager']})]

    def has_module_permission(self, request, obj=None):
        if request.user.is_anonymous: return False
        if request.user.is_superuser or request.user.is_officer: return True
        if super(OfficerAdmin, self).has_module_permission(request, obj):
            return True
        return False

    def has_view_permission(self, request, obj=None):
        # Only superusers or the manager can view the Officer
        if obj is None : return True
        if obj is not None and (request.user.id == obj.manager.id
                                or request.user.is_superuser):
            return True
        return False

    def has_change_permission(self, request, obj=None):
        # Only superusers or the manager can change the Officer
        if obj is None : return True
        if obj is not None and (request.user.id == obj.manager.id
                                or request.user.is_superuser):
            return True
        return False

    def get_list_display(self, request):
        if request.user.is_superuser: 
            if 'manager' not in self.list_display:
                self.list_display.append('manager')
        return self.list_display

    def get_list_filter(self, request, obj=None):
        if request.user.is_superuser: 
            return ['hei__name', 'hei__sho', 'hei__pic', 'hei__oid']
        return []

    def get_exclude(self, request, obj=None):
        # Allow the Superusers to "get rid" of Officers by changing the manager
        if request.user.is_superuser:
            return []
        return ['manager',]
        
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "manager":
            if request.user.is_superuser: 
                # Only the superuser can reassign Officers
                allowed_persons = Person.objects.filter(is_staff=True)
            else:
                allowed_persons = Person.objects.filter(id=request.user.id)
            kwargs["queryset"] = allowed_persons 
        if db_field.name == "hei":
            if request.user.is_superuser:
                allowed_heis = HEI.objects.all()
            else:
                allowed_heis = request.user.HEIs
            kwargs["queryset"] = allowed_heis 
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        if request.user.is_superuser: return Officer.objects.all()
        return Officer.objects.filter(manager=request.user)

    def save_model(self, request, obj, form, change):
        if not change and obj.manager is None:
            obj.manager = request.user
        super().save_model(request, obj, form, change)

    def get_urls(self):
        urls = super().get_urls()
        urls.insert(0, path('officer_load/',
                    self.admin_site.admin_view(self.load_officers)))
        return urls

    def load_officers(self,request):
        """
        A view for loading HEI officers.
        Only superusers can load officers.
        An officer is just a person that has special status and is linked to a HEI
        The first officer for a HEI may be loaded as an unlinked person and the link
        is later established when the HEI is created.
        Officers are uploaded in CSV format with a minimum set of fields:
            - first_name : officer's given name
            - last_name : officer's family name
            - email : officer's email
        Optional fields:
            - identifier : government issued identifier for the person
            - sho : officer's HEI schacHomeOrganization
            SHO is required for linking the officer to the HEI. 
            If there is no HEI, the person is created in the system
            with needed privileges but no associated HEI.
            Persons receive an invitation via email for activating the account.
        """
    
        user = request.user
        #if not user.is_superuser: 
        #    return HttpResponseForbidden(_('Access not permitted'))
        errors = []
        new_persons = []
        if request.method == 'POST':
            # Process the form
            form = officerLoadForm(request.POST, request.FILES)
            # Is the user an officer loading secondary ones?
            if not user.is_superuser:
                hei = request.POST.get('hei', None)
                # If we get a HEI id, it MUST exist, if not, explode mercilessly
                hei = get_object_or_404(HEI, id=hei) if hei is not None else user.myHEI
                # Officers MUST manage the HEI
                officer = user.manages.filter(hei=hei).first()
                # If officer is None, something smells fishy, explode
                if officer is None: 
                    return HttpResponseForbidden(_('Access not permitted'))
            # The "C" in CSV means "Comma",
            # although sometimes Excel thinks it means "semicolon"
            delimiter = request.POST.get('delimiter', ',')
            data = request.FILES['data']
            data.seek(0)
            lines = csv.DictReader(io.StringIO(data.read().decode('utf-8-sig')),
                                   delimiter=delimiter)
            # There must be at least one line and it must contain the required fields
            total = 1
            inserted = 0
            # Let's load the data
            for line in lines:
                total += 1
                errors_in_line = False
                for field in ['first_name', 'last_name', 'email']:
                    if line.get(field, '').strip() == '':
                        errors_in_line = True
                        errors.append(_('Field {0} missing on line {1}').format(field, total))
                if errors_in_line: continue
                # Superusers may indicate the HEI the officers are for
                sho = line.get('sho', None)
                if user.is_superuser and sho is not None:
                    hei = HEI.objects.filter(sho=sho.strip())
                # New or existing person?
                person, new  = Person.objects.get_or_create(email=line['email'].strip())
                if new:
                    person.first_name = line['first_name'].strip()
                    person.last_name = line['last_name'].strip()
                    person.managedBy = request.user
                    new_persons.append((person, hei))
                if new or not person.is_staff:
                    person.is_staff = True
                    person.save()
    
                # We are good, create the Officer if does not exist
                new = not Officer.objects.filter(hei=hei,person=person).exists()
                if new and hei is not None:
                    officer = Officer(hei=hei, person=person, manager=user)
                    officer.save()
                    inserted += 1
            # Data processed, how did it go...
            # At least one officer inserted
            if not inserted == 0:
                self.message_user(request,
                                  ngettext('{0} officer loaded',
                                           '{0} officers loaded',
                                           inserted).format(inserted),
                                  messages.SUCCESS)
            # Person objects created
            newpersons = len(new_persons)
            if not newpersons == 0:
                self.message_user(request,
                                  ngettext('{0} person created',
                                           '{0} persons created',
                                           newpersons).format(newpersons),
                                  messages.SUCCESS)
            # We can send the invites to those that have just been added
            # to the system, asking for consent
            for person in new_persons:
                result = person[0].invite(request.user,
                                          host=request.get_host(),
                                          hei=person[1],
                                          template='esiidm/officer_invite.txt')
                if not result:
                    errors.append(_('Message to {0} not sent').format(person[0].email))
            # All went well, no errors
            if len(errors) == 0:
                return redirect('..')
            for e in errors: 
                self.message_user(request, e, messages.WARNING)
        # Render the form
        if len(errors) == 0:
            # Get a fresh form
            form = officerLoadForm()
            # If officer manages more than one HEI, add a selector
            if len(user.HEIs) > 1:
                choices = [(h.id,h.name) for h in user.HEIs]
                form.fields['hei'] = forms.ChoiceField(label=_('Select HEI'),
                                                       initial=user.myHEI,
                                                       choices=choices)
        context = dict(self.admin_site.each_context(request), form = form)
        return TemplateResponse(request, 'esiidm/load_officers.html', context)


class StudentCardForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "initial" in kwargs:
            officers = Officer.objects.all()
        else:
            officers = Officer.objects.filter(hei=self.instance.hei)
        self.fields['manager'].queryset = officers
        
@admin.register(StudentCard)
class StudentCardAdmin(admin.ModelAdmin):
    form = StudentCardForm
    search_fields = ['student__email', 'student__identifier',
                     'student__last_name', 'esi',]
    list_display = ['esi', 'student']
    list_display_links = ['esi', 'student',]
    select_related = True
    fieldsets = [(None, {'fields': [('student', 'hei'), ('esi', 'esc'),
                         'manager']})]
    readonly_fields = ['esc']
    actions = ['export_cards']

    def has_module_permission(self, request, obj=None):
        if request.user.is_anonymous: return False
        if request.user.is_superuser or request.user.is_officer: return True
        if super(StudentCardAdmin, self).has_module_permission(request, obj):
            return True
        return False

    def has_add_permission(self, request):
        # It doesn't make sense adding indiviual cards, better load them
        return False

    def has_view_permission(self, request, obj=None):
        if obj is None : return True
        # Only the officer managing a card can see it
        if obj is not None and obj.manager.person == request.user:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if obj is None : return True
        # Only the officer managing a card can touch it
        if obj is not None and obj.manager.person == request.user:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if obj is None : return True
        # Only the officer managing a card can touch it
        if obj is not None and obj.manager.person == request.user:
            return True
        return False

    def get_list_display(self, request):
        if request.user.HEIs.count() > 1:
            if 'hei' not in self.list_display:
                self.list_display.insert(0,'hei')
        return self.list_display

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "hei":
            kwargs["queryset"] = request.user.HEIs
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        # Only managed cards will be shown
        return StudentCard.objects.filter(manager__in=request.user.manages.all())

    def save_model(self, request, obj, form, change):
        if not change and obj.manager is None:
            obj.manager = request.user
        super().save_model(request, obj, form, change)

    def get_urls(self):
        urls = super().get_urls()
        urls.insert(0, path('card_load/',
                    self.admin_site.admin_view(self.load_cards)))
        return urls

    def export_cards(self, request, queryset):
        """
        Generates a CSV file with selected student cards.
        """
        response = HttpResponse(content_type='text/csv')
        response.write(codecs.BOM_UTF8)
        response['Content-Disposition'] = 'attachment; filename=cards.csv'

        writer = csv.writer(response)
        writer.writerow(
            [field.verbose_name for field in StudentCard._meta.fields]
        )

        fields_names = [field.name for field in StudentCard._meta.fields]

        for card in queryset.all():
            writer.writerow(
                [
                    card.__getattribute__(field)
                    for field in fields_names
                ]
            )
        return response
    export_cards.short_description = _('Export selected cards to CSV file.')

    def load_cards(self, request):
        """
        A view for loading student cards.
        Only officers can load cards for the HEIs the manage.
        Cards are uploaded in CSV format with a minimum set of fields:
            - esi : contains the student specific part of the ESI
            - first_name : student's given name
            - last_name : student's family name
            - email : student's email
        Optional fields:
            - identifier : government issued identifier for the student
            - operation : if present, value MUST (RFC 2119) be either:
                D for deleting the card if it belongs to the student
                C for creating a new card, this is the default if absent
        Persons are created as needed and receive an invitation over email
        requesting consent.
        """
    
        user = request.user
        if not request.user.is_officer: 
            return HttpResponseForbidden(_('Access not permitted'))
        # Once we are clear, the user can use and the method is right, let's work
        errors = []
        if request.method == 'POST':
            # Process the form
            form = cardLoadForm(request.POST, request.FILES)
            # Most common use case is just one HEI for an officer
            hei = request.POST.get('hei', None)
            # The "C" in CSV means "Comma",
            # although sometimes Excel thinks it means "semicolon"
            delimiter = request.POST.get('delimiter', ',')
            # If we get a HEI id, it MUST exist, if not, explode mercilessly
            hei = get_object_or_404(HEI, id=hei) if hei is not None else user.myHEI
            # Officers MUST manage the HEI
            officer = user.manages.filter(hei=hei).first()
            # If officer is None, something smells fishy, explode
            if officer is None: 
                return HttpResponseForbidden(_('Access not permitted'))
            data = request.FILES['data']
            data.seek(0)
            lines = csv.DictReader(io.StringIO(data.read().decode('utf-8-sig')),
                                   delimiter=delimiter)
            # There must be at least one line and it must contain the required fields
            # And the load operation has to succeed for the whole file
            total = 1
            cards = 0
            deleted = 0
            new_persons = []
            new_cards = []
            with transaction.atomic():
                try:
                    for line in lines:
                        errors_in_line = False
                        esi = line.get('esi', None)
                        email = line.get('email', None)
                        first_name = line.get('first_name', None)
                        last_name = line.get('last_name', None)
                        # If any required field is missing, abort
                        if ( esi in (None, '') or
                             email in (None, '') or
                             first_name in (None, '') or
                             last_name in (None, '')):
                            errors_in_line = True
                            total += 1
                            errors.append(_('Missing data on line {0}').format(total))
                        opcode = line.get('operation','C')
                        if opcode is None or opcode.strip() == '': opcode = 'C'
                        if opcode not in ['C', 'D']:
                            error = True
                            total += 1
                            errors.append(_('Bad operation {0} on line {1}').format(opcode, total))
                        if errors_in_line: continue
                        if opcode == 'C':
                            person, new = Person.objects.get_or_create(email=email.strip())
                            if new:
                                person.first_name = first_name.strip()
                                person.last_name = last_name.strip()
                                person.managedBy = user
                                person.save()
                                new_persons.append(person.pk)
                            # There MUST be one card per person per hei and esi
                            card = StudentCard.objects.filter(student = person,
                                                              hei = hei,
                                                              esi = esi.strip()).first()
                            newcard = False
                            if card is None:
                                newcard = True
                                card = StudentCard()
                                card.student = person
                                card.hei = hei
                                card.esi = esi.strip()
                            # Cards will be assigned to the officer loading them
                            # this eases the process for transfering control of
                            # existing cards by just reloading the transferred ones
                            card.manager = officer
                            card.save()
                            # We make a note of newly created cards
                            # for persons that were already known to the system
                            if newcard and not new: new_cards.append(card.pk)
                            total += 1
                        if opcode == 'D':
                            # There MUST be one card per person per hei and esi
                            card = StudentCard.objects.filter(hei = hei,
                                                              esi = esi.strip()).first()
                            if card is None:
                                errors.append(_('Card not found on line {0}').format(total))
                                continue
                            card.delete()
                            deleted += 1
                    # Data had problems, raise an exception, forcing a roll back
                    if not len(errors) == 0:
                        raise RuntimeError(_('Data has errors'))
                except RuntimeError as error: 
                    for e in errors: 
                        self.message_user(request, e, messages.ERROR)
            # Transactional part succeeded
            # Lines processed are total minus the header
            total -= 1
            # We can send the invites to those that have just been added
            # to the system, asking for consent
            host = get_setting('MAIL_ORIGIN_DOMAIN',
                               request.get_host().split(':')[0])
            for person in Person.objects.filter(id__in = new_persons):
                result = person.invite(request.user, hei=hei, host=host)
                if not result:
                    errors.append(_('Message to {0} not sent').format(person.email))
            if not total == 0:
                if not len(new_persons) == 0:
                    npersons = len(new_persons)
                    self.message_user(request,
                                      ngettext('{0} person added',
                                               '{0} persons added',
                                               npersons).format(npersons),
                                      messages.SUCCESS)
                if not len(new_cards) == 0 or not len(new_persons) == 0:
                    # Cards are added for existing and new persons
                    ncards = len(new_cards) + len(new_persons)
                    self.message_user(request,
                                      ngettext('{0} card added',
                                               '{0} cards added',
                                               ncards).format(ncards),
                                      messages.SUCCESS)
                if not deleted == 0:
                    self.message_user(request,
                                      ngettext('{0} card deleted',
                                               '{0} cards deleted',
                                               deleted).format(deleted),
                                      messages.SUCCESS)
        # Render the form
        if len(errors) == 0:
            # Get a fresh form
            form = cardLoadForm()
            # If officer manages more than one HEI, add a selector
            if len(user.HEIs) > 1:
                choices = [(h.id,h.name) for h in user.HEIs]
                form.fields['hei'] = forms.ChoiceField(label=_('Select HEI'),
                                                       initial=user.myHEI,
                                                       choices=choices)
        context = dict(self.admin_site.each_context(request), form = form)
        return TemplateResponse(request, 'esiidm/load_cards.html', context)



@admin.register(IdSource)
class IdSourceAdmin(admin.ModelAdmin):
    search_fields = ['source', 'attribute',]
    list_display = ['source', 'active', 'attribute', 'extractor', 'description']
    list_editable = ['active']
    list_filter = ['active']
    list_display_links = ['source', ]
    readonly_fields = ['source', 'attribute', 'extractor']
    fieldsets = [(None, {'fields': [('source', 'attribute'), 'extractor',
                                    'active', 'description']})]

