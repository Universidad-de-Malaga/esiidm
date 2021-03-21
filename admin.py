# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$

from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ngettext
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.conf import settings

# Register your models here.
from .models import HEI, Person, Officer, StudentCard, IdSource, Identifier
from .forms import cardLoadForm, heiLoadForm, officerLoadForm

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


class IdentifierInline(admin.TabularInline):
    model = Identifier
    hidden_fields = ('id')

    def has_view_permission(self, request, obj=None):
        if not super(IdentifierAdmin, self).has_view_permission(request, obj):
            return False
        if obj is None : return True
        # Not even superusers should view Identifiers for
        # Persons they do not manage
        if obj is not None and request.user.id == obj.person.managedBy.id:
            return True
        # Persons with admin privileges can view their data
        if obj is not None and request.user.id == obj.person.id:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        # Nobody may change identifier data, it has to happen from an invite
        return False


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    #list_filter = ['has_accepted']
    search_fields = ['email', 'identifier', 'last_name']
    list_display_links = ['email', 'identifier', 'last_name']
    list_display = ['email', 'identifier', 'last_name', 'has_accepted']
    inlines = [ IdentifierInline ]

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

    def has_view_permission(self, request, obj=None):
        if not super(PersonAdmin, self).has_view_permission(request, obj):
            return False
        if obj is None : return True
        # Not even superusers should view Persons they do not manage
        if obj is not None and request.user.id == obj.managedBy.id:
            return True
        # Persons with admin privileges can view their data
        if obj is not None and request.user.id == obj.id:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if not super(PersonAdmin, self).has_change_permission(request, obj):
            return False
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

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = []
        if not request.user.is_superuser and request.user.is_officer:
            readonly_fields = []
        return readonly_fields

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
                                                   'fields': [('last_login',
                                                               'date_joined')
                                                             ]}))
        return fieldsets


@admin.register(HEI)
class HEIAdmin(admin.ModelAdmin):
    list_filter = [CountryListFilter]
    search_fields = ['name', 'pic', 'euc', 'sho']
    list_display = ['name', 'pic', 'sho', 'url', 'erc']
    list_display_links = ['name', 'pic', 'sho']
    #change_list_template = 'esiidm/hei_changelist.html'

    def has_view_permission(self, request, obj=None):
        if not super(HEIAdmin, self).has_view_permission(request, obj):
            return False
        # Only superusers or the manager for the HEI can view a HEI
        if obj is None : return True
        if obj is not None and (request.user.id == obj.managedBy.id
                                or request.user.is_superuser):
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if not super(HEIAdmin, self).has_change_permission(request, obj):
            return False
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
            readonly_fields = ['name', 'country', 'url', 
                               'pic', 'sho', 'euc', 'erc']
        return readonly_fields

    def get_fieldsets(self, request, obj=None):
        # Adapt the field sets depending on who's managing the person
        # (_(''), {'fields': []}),
        fieldsets = [(None, {'fields': [('name', 'country', 'url'),
                                        'termstart',]}),
                     (_('Erasmus'), {'fields': [('pic', 'euc'),
                                                ('erc', 'sho')]}),
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
            - pic : HEI PIC code
            - euc : HEI EUC code
            - erc : HEI Erasmus code
            - sho : SCHAC Home Organization (HEI Internet domain)
        Optional fields:
            - url : HEI main web page
            - termstart : month when term starts (1 through 12)
            - manager : email address for the main HEI officer
        """
    
        user = request.user
        if not user.is_superuser: 
            return HttpResponseForbidden(_('Access not permitted'))
        errors = []
        if request.method == 'POST':
            # Process the form
            form = heiLoadForm(request.POST, request.FILES)
            #if not form.is_valid():
            #    return render(request, 'esiidm/load_heis.html', {'form': form})
            data = request.FILES['data']
            data.seek(0)
            lines = csv.DictReader(io.StringIO(data.read().decode('utf-8')))
            # There must be at least one line and it must contain the required fields
            total = 1
            inserted = 0
            # Let's load the data
            for line in lines:
                total += 1
                errors_in_line = False
                for field in ['name', 'country', 'pic', 'euc', 'erc', 'sho']:
                    if line.get(field, '').strip() == '':
                        errors_in_line = True
                        errors.append(_(f'Field {field} missing on line {total}'))
                if errors_in_line: continue
                manager_mail = line.get('manager', '').strip()
                manager = Person.objects.filter(email=manager_mail).first()
                # Do we have a main manager?
                if manager is None:
                    e = _(f'Manager {manager_mail} in line {total} does not exist')
                    errors.append(e)
                    continue
                # We are good, create the HEI if it does not exist
                hei, new  = HEI.objects.get_or_create(pic=line['pic'],
                                                      euc=line['euc'],
                                                      erc=line['erc'])
                if not new:
                    e = _(f'{hei} already exists in line {total}')
                    errors.append(e)
                    continue
                hei.manager = manager
                hei.name = line['name']
                hei.country = line['country']
                hei.sho = line['sho']
                hei.url = line.get('url', '')
                hei.termstart = line.get('termstart',
                                         settings.__dict__.get('TERM_START', 9))
                try:
                    hei.save()
                    inserted += 1
                except:
                    e = _(f'{hei} in line {total} not saved. Existing data.')
                    errors.append(e)
                    continue
            # Data processed, how did it go...
            # At least one HEI inserted
            if not inserted == 0:
                self.message_user(request,
                                  ngettext(f'{inserted} HEI loaded',
                                           f'{inserted} HEIs loaded',
                                           inserted),
                                  messages.SUCCESS)
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
    list_filter = ['hei__name', 'hei__sho', 'hei__pic']
    list_filter_select = True
    select_related = True
    search_fields = ['person__email', 'hei__pic', 'hei__euc', 'hei__sho']
    list_display = ['person',]
    list_display_links = ['person',]
    fieldsets = [(None, {'fields': [('person', 'hei'), 'manager']})]
    #change_list_template = 'esiidm/officer_changelist.html'

    def has_view_permission(self, request, obj=None):
        if not super(OfficerAdmin, self).has_view_permission(request, obj):
            return False
        # Only superusers or the manager can view the Officer
        if obj is None : return True
        if obj is not None and (request.user.id == obj.manager.id
                                or request.user.is_superuser):
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if not super(OfficerAdmin, self).has_change_permission(request, obj):
            return False
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
            - pic : officer's HEI PIC code
            - euc : officer's HEI EUC code
            - erc : officer's HEI ERC code
            Only one of PIC, EUC or ERC is required for linking the officer
            to the HEI. If there is no HEI, the person is created in the system
            with needed privileges but no associated HEI.
            Persons receive an invitation via email for activating the account.
        """
    
        user = request.user
        if not user.is_superuser: 
            return HttpResponseForbidden(_('Access not permitted'))
        errors = []
        new_persons = []
        if request.method == 'POST':
            # Process the form
            form = officerLoadForm(request.POST, request.FILES)
            #if not form.is_valid():
            #    return render(request, 'esiidm/load_officers.html', {'form': form})
            data = request.FILES['data']
            data.seek(0)
            lines = csv.DictReader(io.StringIO(data.read().decode('utf-8')))
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
                        errors.append(_(f'Field {field} missing on line {total}'))
                if errors_in_line: continue
                hei = HEI.object.filter(Q(pic=line.get('pic', None))|
                                        Q(euc=line.get('euc', None))|
                                        Q(erc=line.get('erc', None))).first()
                # Do we have a HEI?
                if hei is None:
                    errors.append(_(f'Wrong HEI on line {total}'))
                    continue
                # New or existing person?
                person, new  = Person.objects.get_or_create(email=line['email'])
                if new:
                    person.first_name = line['first_name']
                    person.last_name = line['last_name']
                    person.managedBy = request.user
                    person.save()
                    new_persons.append(person.id)
    
                # We are good, create the Officer
                officer, new  = Officer.objects.get_or_create(hei=hei,
                                                              person=person)
                if new:
                    officer.manager = request.user
                    officer.save()
                    inserted += 1
            # Data processed, how did it go...
            # At least one officer inserted
            if not inserted == 0:
                self.message_user(request,
                                  ngettext(f'{inserted} officer loaded',
                                           f'{inserted} officers loaded',
                                           inserted),
                                  messages.SUCCESS)
            # We can send the invites to those that have just been added
            # to the system, asking for consent
            for person in Person.objects.filter(id__in = new_persons):
                person.invite(request.user, template='esiidm/officer_invite.txt')
            # All went well, no errors
            if len(errors) == 0:
                return redirect('..')
            for e in errors: 
                self.message_user(request, e, messages.WARNING)
        # Render the form
        if len(errors) == 0:
            # Get a fresh form
            form = officerLoadForm()
        context = dict(self.admin_site.each_context(request), form = form)
        return TemplateResponse(request, 'esiidm/load_officers.html', context)


@admin.register(StudentCard)
class StudentCardAdmin(admin.ModelAdmin):
    search_fields = ['student__email', 'student__identifier', 'esi',]
    list_display = ['esi', 'student']
    list_display_links = ['esi', 'student',]
    select_related = True
    fieldsets = [(None, {'fields': [('student', 'hei'), ('esi', 'esc'),
                         'manager']})]
    readonly_fields = ['esc']

    def has_add_permission(self, request):
        if not super(StudentCardAdmin, self).has_add_permission(request):
            return False
        return True

    def has_view_permission(self, request, obj=None):
        if obj is None : return True
        # Only the officer managing a card can see it
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
        Persons are created as needed and recive an invitation over email
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
            #if not form.is_valid():
            #    return render(request, 'esiidm/load_cards.html', {'form': form})
            # Most common use case is just one HEI for an officer
            hei = form.cleaned_data.get('hei', None)
            # If we get e HEI id, it MUST exist, if not, explode mercilessly
            hei = get_object_or_404(HEI, id=hei) if hei is not None else user.myHEI
            # Officers MUST manage the HEI
            officer = user.manages.filter(hei=hei).first()
            # If officer is None, something smells fishy, explode
            if officer is None: 
                return HttpResponseForbidden(_('Access not permitted'))
            data = request.FILES['data']
            data.seek(0)
            lines = csv.DictReader(io.StringIO(data.read().decode('utf-8')))
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
                        esi = line.get('esi', None)
                        email = line.get('email', None)
                        first_name = line.get('first_name', None)
                        last_name = line.get('last_name', None)
                        # If any required field is missing, abort
                        if ( esi in (None, '') or
                             email in (None, '') or
                             first_name in (None, '') or
                             last_name in (None, '')):
                            total += 1
                            errors.append(_(f'Missing data on line {total}: {line}'))
                        opcode = line.get('operation','C')
                        if opcode not in ['C', 'D']:
                            total += 1
                            errors.append(_(f'Bad operation {opcode} on line {total}'))
                        if opcode == 'C':
                            person, new = Person.objects.get_or_create(email=email)
                            if new:
                                person.first_name = first_name
                                person.last_name = last_name
                                person.managedBy = user
                                person.save()
                                new_persons.append(person.pk)
                            card, newcard = StudentCard.objects.get_or_create(
                                                                   person = person,
                                                                   hei = hei,
                                                                   esi = esi)
                            # Cards will be assigned to the officer loading them
                            # this eases the process for transfering control of
                            # existing cards by just reloading the transferred ones
                            card.manager = officer
                            card.save()
                            # We make a note of newly created cards
                            # for persons that were already known to the system
                            if newcard and not newperson: new_cards.append(card.pk)
                            total += 1
                    # Data had problems, raise an exception, forcing a roll back
                    if not len(errors) == 0:
                        raise RuntimeError(_('Data has errors'))
                except RuntimeError as error: 
                    for e in errors: 
                        self.message_user(request, e, messages.ERROR)
            # Transactional part succeeded
            # Lines processed are total minus the header
            total -= 1
            if not total == 0:
                self.message_user(request,
                                  ngettext(f'{total} line processed',
                                           f'{total} lines processed',
                                           total),
                                  messages.SUCCESS)
            # We can send the invites to those that have just been added
            # to the system, asking for consent
            for person in Person.objects.filter(id__in = new_persons):
                person.invite(request.user, hei=hei)
        # Render the form
        if len(errors) == 0:
            # Get a fresh form
            form = heiLoadForm()
        context = dict(self.admin_site.each_context(request), form = form)
        return TemplateResponse(request, 'esiidm/load_cards.html', context)



@admin.register(IdSource)
class IdSourceAdmin(admin.ModelAdmin):
    search_fields = ['source', 'attribute',]
    list_display = ['source', 'attribute', 'extractor']
    list_editable = ['attribute', 'extractor']
    list_display_links = ['source', ]
    fieldsets = [(None, {'fields': [('source', 'attribute'), 'extractor']})]

