# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$
"""
Authentication based on HTTP server environment variables for Cl@ve.

Implemented using mod_auth_mellon for SAML2 authentication.

"""
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

import hashlib

source_name = 'clave'
source_attribute = 'MELLON_PersonIdentifier_0'
extractor = '.*'
description = _('HTTP server environment variables based authentication for Cl@ve')

def authn(request):
    # Who's using us?
    attribute = request.META.get(source_attribute, None)
    if attribute is None:
        request.session.flush()
        return HttpResponseForbidden(_('Access not permitted'))
    # All OK, we have an authenticated user from the server
    # We save hashes, minimising PII
    attribute = hashlib.sha512(attribute.encode('utf8')).hexdigest().upper()
    request.session['authn_source'] = source_name
    request.session['authn_attribute'] = attribute
    # Let's continue the authentication flow
    request.session['authn_phase'] = 'login'
    return redirect(reverse('esiidm:authenticate'))
