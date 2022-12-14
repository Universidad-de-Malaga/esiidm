# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$
"""
This is a simple token over email authentication mechanism.

If the session contains the requesting user,
it simply sends the token to the person known email address.

If there is no user, request an email address,
find the corresponding person and send the token.

Finally, show a form for entering the token the user should have received.
"""

from django.shortcuts import render
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.signing import TimestampSigner
from django.core.signing import SignatureExpired
from django.core.signing import BadSignature
from django.http import HttpResponseForbidden
from django.urls import reverse
from django import forms

from esiidm.models import Person, IdSource

import uuid

# Mandatory module attributes for the management interface
# No attribute and no extractor regular expression
source_name = 'mail'
source_attribute = _('No source, extractor is time duration')
extractor = '5'
description = _('Email token based authentication')

class mailForm(forms.Form):
    email = forms.EmailField(max_length=100)

class tokenForm(forms.Form):
    token = forms.CharField(max_length=128)

def _send_token(person, token, host, url, time=int(extractor)):
    """
    Internal module function to send a short lived token to a person.
    It does not belong in the person model, as it is something particular
    to this authentication method.
    """
    signer = TimestampSigner()
    token = signer.sign(token)
    msg = EmailMessage()
    msg.to = [f'"{person.first_name} {person.last_name}" <{person.email}>']
    hei = person.myHEI
    name = '' if hei is None else hei.name
    msg.from_email = _('Authentication system for {0} <no-reply@{1}>').format(name, host)
    msg.subject = _('Your access token for {0} card management system').format(name)
    msg.extra_headers = {'Message-Id': '{}@esiidm'.format(uuid.uuid4())}
    # This is a simple message, and it is better if the module has as few
    # external files as possible. And it can be used as a format string.
    msg.body = _("""
    {0} {1}

    You are accessing {2}, that requires that you authenticate with
    the following token in the next {3} minutes.

    Token: {4}

    You can copy it and paste on the form that has informed you about
    this message.

    Thank you.

    """).format(person.first_name, person.last_name, url, time, token)
    try:
        msg.send()
        return True
    except:
        # Token could not be sent
        return False
    
    
def authn(request):
    # Do we have someone to authenticate?
    person_id = request.session.get('person', None)
    person = False
    result = False
    if person_id is not None:
        person = Person.objects.filter(pk=person_id).first()
        if not person:
            # Something is wierd ...
            request.session.flush()
            return HttpResponseForbidden(_('Access not permitted'))
    if request.method == 'GET':
        if person:
            # Person is known to the system, no need to request an email
            token = uuid.uuid4().hex
            request.session['token'] = token
            phase = 'final'
            result = _send_token(person, token,
                                 host = request.get_host().split(':')[0],
                                 url = request.session.get('next', ''))
            form = tokenForm()
        else:
            # We need an email to check that person is known to the system
            phase = 'ask'
            form = mailForm()
        request.session['mail_phase'] = phase
        return render(request, 'esiidm/auth/mail.html',
                      {'form': form, 'phase': phase, 'result': result})
    if request.method == 'POST':
        phase = request.session.get('mail_phase', None)
        if phase is None:
            # We should not reach here with no phase, something smells fishy
            request.session.flush()
            return HttpResponseForbidden(_('Access not permitted'))
        if phase == 'final':
            saved_token = request.session.get('token', None)
            if saved_token is None:
                # No token in session? Something smells fishy
                request.session.flush()
                return HttpResponseForbidden(_('Access not permitted'))
            received_token = request.POST.get('token', None)
            if received_token is None:
                # No token from from? Something smells fishy
                request.session.flush()
                return HttpResponseForbidden(_('Access not permitted'))
            person_id = request.session.get('person', None)
            person = Person.objects.filter(pk=person_id).first()
            if person is None:
                # No person in the session? Something smells fishy
                request.session.flush()
                return HttpResponseForbidden(_('Access not permitted'))
            signer = TimestampSigner()
            try:
                age = int(extractor)
                received_token = signer.unsign(received_token, max_age=age*60)
            except SignatureExpired:
                form = tokenForm()
                result = _send_token(person, saved_token,
                                     host = request.get_host().split(':')[0],
                                     url = request.session.get('next', ''))
                return render(request, 'esiidm/auth/mail.html',
                              {'form': form, 'phase': phase,
                               'result': result, 'expired': True})
            except BadSignature:
                request.session.flush()
                return HttpResponseForbidden(_('Access not permitted'))
            if not received_token == saved_token:
                request.session.flush()
                return HttpResponseForbidden(_('Access not permitted'))
            # All OK, the person is authenticated
            request.session['authn_source'] = source_name
            request.session['authn_attribute'] = 'token'
            # Let's continue the authentication flow
            request.session['authn_phase'] = 'login'
            return redirect(reverse('esiidm:authenticate'))
        if phase == 'ask':
            email = request.POST.get('email', None)
            if email is None:
                # No email from from? Something smells fishy
                request.session.flush()
                return HttpResponseForbidden(_('Access not permitted'))
            person = Person.objects.filter(email=email).first()
            if person is not None:
                # If we know the email, send a token, if not, we don't care
                token = uuid.uuid4().hex
                request.session['token'] = token
                request.session['person'] = person.id
                result = _send_token(person, token,
                                     host = request.get_host().split(':')[0],
                                     url = request.session.get('next', ''))
            form = tokenForm()
            phase = 'final'
            request.session['mail_phase'] = phase
            return render(request, 'esiidm/auth/mail.html',
                          {'form': form, 'phase': phase, 'result': True})

    # If we reach here, there is no authenticated user
    request.session.flush()
    return HttpResponseForbidden(_('Access not permitted'))
