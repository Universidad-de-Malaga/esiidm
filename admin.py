# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$

from django.contrib import admin
from django.db.models import Q

# Register your models here.
from .models import HEI, Person, Officer, StudentCard

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    #list_filter = ['has_accepted']
    search_fields = ['email', 'identifier', 'last_name']
    list_display_links = ['email', 'identifier', 'last_name']
    list_display = ['email', 'identifier', 'last_name', 'has_accepted']

    def get_exclude(self, request, obj=None):
        # Allow the Superusers to "get rid" of people by changing the manager
        if request.user.is_superuser:
            return []
        return ['managedBy',]
        
    def get_display(self, request, obj=None):
        # Is the user a superuser or an officer for several HEIs
        if request.user.is_superuser or (request.user.is_officer and
                                         len(user.heis.all()) > 1):
            list_display.append('myHEI')
        return list_display

    def has_change_permission(self, request, obj=None):
        if not super(PersonAdmin, self).has_change_permission(request, obj):
            return False
        # Not even superusers should alter Persons they do not manage
        if obj is not None and request.user.id != obj.managedBy.id:
            return False
        return True

    def queryset(self, request):
        if request.user.is_superuser: return Person.objects.all()
        return Person.objects.filter(managedBy=request.user)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.managedBy = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "managedBy":
            kwargs["queryset"] = Person.objects.filter(is_staff)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(HEI)
class HEIAdmin(admin.ModelAdmin):
    list_filter = ['country']
    search_fields = ['name', 'pic', 'euc', 'sho']

    def get_exclude(self, request, obj=None):
        # Allow the Superusers to "get rid" of people by changing the manager
        if request.user.is_superuser:
            return []
        return ['managedBy',]
        
    def has_change_permission(self, request, obj=None):
        if not super(HEIAdmin, self).has_change_permission(request, obj):
            return False
        return True

    def get_list_display(self, request, obj=None):
        list_display = ['name', 'pic', 'sho', 'url', 'erc']
        # Is the user a superuser or an officer for several HEIs
        if request.user.is_superuser: 
            list_display.insert(0,'country')
            list_display.insert(2,'managedBy')
        return list_display

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "managedBy":
            kwargs["queryset"] = Person.objects.filter(is_staff)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        if request.user.is_superuser: return HEI.objects.all()
        return HEI.objects.filter(managedBy=request.user)

    def save_model(self, request, obj, form, change):
        if not change and obj.managedBy is None:
            obj.managedBy = request.user
        super().save_model(request, obj, form, change)


@admin.register(Officer)
class OfficerAdmin(admin.ModelAdmin):
    list_filter = ['hei__country', 'hei__name', 'hei__sho', 'hei__pic']
    list_filter_select = True
    search_fields = ['person__email', 'hei__pic', 'hei__euc', 'hei__sho']
    list_display = ['person',]
    list_display_links = ['person',]

    def has_change_permission(self, request, obj=None):
        if not super(OfficerAdmin, self).has_change_permission(request, obj):
            return False
        return True

    def get_list_display(self, request):
        if request.user.is_superuser: 
            list_display.append('manager')
        return list_display

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "manager":
            if request.user.is_superuser: 
                # Only the superuser can reassign Officers
                allowed_persons = Person.objects.filter(is_staff)
            else:
                allowed_persons = Person.objects.filter(id=request.user.id)
            kwargs["queryset"] = allowed_persons 
        if db_field.name == "hei":
            if request.user.is_superuser:
                allowed_heis = HEI.objects.all()
            else:
                allowed_heis = request.user.heis.all()
            kwargs["queryset"] = allowed_heis 
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        if request.user.is_superuser: return Officer.objects.all()
        return Officer.objects.filter(manager=request.user)

    def save_model(self, request, obj, form, change):
        if not change and obj.manager is None:
            obj.manager = request.user
        super().save_model(request, obj, form, change)


@admin.register(StudentCard)
class StudentCardAdmin(admin.ModelAdmin):
    search_fields = ['person__email', 'person__identifier', 'esi',]
    list_display = ['esi', 'person']
    list_display_links = ['esi', 'person',]

    def has_change_permission(self, request, obj=None):
        # Only the officer managing a card can touch it
        if obj is not None and obj.manager.person == request.user:
            return True
        return False

    def get_list_display(self, request):
        if len(request.person.heis.all()) > 1:
            list_display.insert(0,'hei')
        return list_display

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        # Only managed cards will be shown
        return Person.objects.filter(manager=request.user)

    def save_model(self, request, obj, form, change):
        if not change and obj.manager is None:
            obj.manager = request.user
        super().save_model(request, obj, form, change)


