# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$
from django.apps import AppConfig


class EsiidmConfig(AppConfig):
    name = 'esiidm'
    verbose_name = 'Eurpean Student Identifier Identity Management'

    def ready(self):
        # Load the authentication modules in the admin
        from .models import IdSource
        import pkgutil
        import esiidm.auth
        modules = []
        for i,name,p in pkgutil.iter_modules(esiidm.auth.__path__):
            m = i.find_module(name).load_module(name)
            modules.append(name)
            source, new = IdSource.objects.get_or_create(source=name)
            if new:
                source.attribute = m.source_attribute
                source.extractor = m.extractor
                source.description = m.description
                source.save()
        del(i)
        del(name)
        del(p)
        del(m)
        # Remove sources that do not have a module implementing them
        #IdSource.objects.exclude(source__in=modules).delete()

