# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$
"""
Authentication based on the hability of the hosting HTTP server to validate
users with X.509 based certificates and setting environment variables with 
certificate data.

The environment variable for the X.509 DN is SSL_CLIENT_S_DN for Apache.

If you use a different httpd server, adapt accordingly.
"""

from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse

import hashlib

source_name = 'x509'
source_attribute = 'SSL_CLIENT_S_DN'
extractor = '.*'
description = 'HTTP server x509 certificate authentication'

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
