# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$

from django.http import HttpResponseForbidden

from esiidm.models import IdSource

def authn(request, method):
    # First check that method exists and is active
    source = IdSource.objects.filter(source=method, active=True)
    if not source:
        request.session.flush()
        return HttpResponseForbidden
    # Method OK, lets load its module and pass control
    m = __import__(method)
    return m(request)
