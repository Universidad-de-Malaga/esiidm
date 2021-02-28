# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$

from django.contrib import admin
from django.db.models import Q

# Register your models here.
from .models import HEI, Person, Officer, StudentCard

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


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    #list_filter = ['has_accepted']
    search_fields = ['email', 'identifier', 'last_name']
    list_display_links = ['email', 'identifier', 'last_name']
    list_display = ['email', 'identifier', 'last_name', 'has_accepted']

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

    def get_exclude(self, request, obj=None):
        # Allow the Superusers to "get rid" of people by changing the manager
        if request.user.is_superuser:
            return []
        return ['managedBy',]
        
    def get_display(self, request, obj=None):
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


@admin.register(HEI)
class HEIAdmin(admin.ModelAdmin):
    list_filter = [CountryListFilter]
    search_fields = ['name', 'pic', 'euc', 'sho']
    list_display = ['name', 'pic', 'sho', 'url', 'erc']
    list_display_links = ['name', 'pic', 'sho']

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
        # Only superusers or the manager for the HEI can view a HEI
        if obj is not None and (request.user.id == obj.managedBy.id
                                or request.user.is_superuser):
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
        return HEI.objects.filter(managedBy=request.user)

    def save_model(self, request, obj, form, change):
        if not change and obj.managedBy is None:
            obj.managedBy = request.user
        super().save_model(request, obj, form, change)


@admin.register(Officer)
class OfficerAdmin(admin.ModelAdmin):
    list_filter = ['hei__name', 'hei__sho', 'hei__pic']
    list_filter_select = True
    select_related = True
    search_fields = ['person__email', 'hei__pic', 'hei__euc', 'hei__sho']
    list_display = ['person',]
    list_display_links = ['person',]

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


@admin.register(StudentCard)
class StudentCardAdmin(admin.ModelAdmin):
    search_fields = ['student__email', 'student__identifier', 'esi',]
    list_display = ['esi', 'student']
    list_display_links = ['esi', 'student',]
    select_related = True

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


