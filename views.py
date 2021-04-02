# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.conf import settings
from django.core.signing import TimestampSigner
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as pgettext
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q

from .models import IdSource, Identifier, Person
from .utils import get_setting

def authenticate(request):
    """
    This view logs the user in, using data in the session that
    has been loaded by one of the authentication modules.
    """
    # We keep the step that started the login flow in the session
    if request.session.get('next', None) is None:
        request.session['next'] = request.GET.get('next',
                                                  reverse('esiidm:start')) 
    phase = request.session.get('authn_phase', None)
    if phase is None:
        # Signal we are starting the login process
        request.session['authn_phase'] = 'start'
        # Get active authentication sources
        sources = IdSource.objects.filter(active=True)
        return render(request, 'esiidm/auth_sources.html',
                      {'sources': sources})
    if phase == 'login':
        # We are back from an authentication source
        # The session may contain either a token or the id for the person
        person_id = request.session.get('person', None)
        otp = request.session.get('otp', None)
        if person_id is None and otp is None:
            # Something smells fishy...
            return HttpResponseForbidden
        if person_id is None and otp is not None:
            # We have a token for a person
            # Get the person
            person = get_object_or_404(Person, otp=otp)
            # Signal that linking is required
            request.session['authn_phase'] = 'link'
        if person_id is not None and otp is None:
            # Get the person
            person = get_object_or_404(Person, pk=person_id)
            # Signal that the person is already know
            request.session['authn_phase'] = 'end'
        # Log the person in
        login(request, person)
        return redirect(request.session.get('next', reverse('esiidm:start')))
    # How did we get here? Someone is messing with the session ...
    return HttpResponseForbidden


def accept(request, otp, response=None):
    """
    This view initiates the consent process once someone receives
    an invitation as student or officer.
    """
    # Check is the otp is still valid
    signer = TimestampSigner()
    try:
        # We allow for an extra hour
        age = get_setting('INVITE_MAX_HOURS', 25)
        opt = signer.unsign(otp, max_age=60*60*age)
    except SignatureExpired:
        # The token is expired, but is otherwise valid
        otp = signer.unsign(otp)
        # The OTP should point to known person, if not, we just explode
        person = Person.object.get(otp=otp)
        # Session should start anew
        request.session.flush()
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
        return render(request,'esiidm/expired.html', {'sent': result})
    except BadSignature:
        request.session.flush()
        return HttpResponseForbidden()
    request.session['otp'] = otp
    # The OTP allows us to get the relevant user,
    # but is not verified by a login process
    if not request.user.is_authenticated:
       return redirect(f'{settings.LOGIN_URL}?next={request.path}') 
    # The user should be authenticated now
    phase = request.session.get('authn_phase', None)
    source = request.session.get('authn_source', None)
    attribute = request.session.get('authn_attribute', None)
    person = request.user
    if phase is None or source is None or attribute is None:
        # Someone is messing with the session ...
        return HttpResponseForbidden
    if phase == 'link':
        # We know how the person has authenticated, we can inform about it
        idsource = get_object_or_404(IdSource, source=source)
        # We need to add an Identifier for the Person
        if response is None and not person.has_accepted:
            # The person has not consented yet
            return render(request, 'esiidm/consent.html', {'source': source})
        if response == 'Y' or person.has_accepted:
            # We need a new identifier
            identifier, new = Identifier(source=idsource,
                                         person=person,
                                         value=attribute)
            if not person.has_accepted:
                # Mark person has consented
                person.acceptedOn = timezone.now()
                person.save()
            return redirect(reverse('esiidm:start'))
        if response == 'N':
            # The person does not consent to the requested operation
            request.session.flush()
            logout(request)
            return render('esiidm/not_consent.html')
    if phase == 'end':
        # The person reused a still valid token, nothing to do
        return redirect(reverse('esiidm:start'))
    # Flow should not reach here, just go back to square one
    request.session.flush()
    logout(request)
    return redirect(reverse('esiidm:start'))

def start(request):
    """
    This is the view that generates the main page.
    If the person has authenticated (i.e. there is a user in the request)
    and has consented to the data being processed by the system, present
    the know PII as student cards in case of students, or just an informative
    page.
    If the autheticated person has not consented or has not authenticated,
    just inform about the options.
    """
    template = 'index.html' if request.user.is_authenticated else 'unkown.html'
    return render(template)


