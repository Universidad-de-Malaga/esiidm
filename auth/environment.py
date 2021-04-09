# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$
"""
Authentication based on HTTP server environment variables.

This is useful, for example, for SAML based authentications using Apache's
mod_auth_mellon or mod_shib.

"""
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse

import hashlib

source_name = 'environment'
source_attribute = 'WHATEVER'
extractor = '.*'
description = 'HTTP server environment variables based authentication'

def authn(request):
    # Who's using us?
    attribute = request.META.get(source_attribute, None)
    if dn is None:
        request.session.flush()
        return HttpResponseForbidden(_('Access not permitted'))
    # All OK, we have an authenticated user from the server
    # We save hashes, minimising PII
    attribute = hashlib.sha512(attribute).hexdigest().upper()
    request.session['authn_source'] = source_name
    request.session['authn_attribute'] = attribute
    # Let's continue the authentication flow
    request.session['authn_phase'] = 'login'
    return redirect(reverse('esiidm:authenticate'))
