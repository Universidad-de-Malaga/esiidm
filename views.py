# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.conf import settings
from django.core.signing import TimestampSigner
from django.core.signing import SignatureExpired
from django.core.signing import BadSignature
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as pgettext
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.http import HttpResponse
from django.http import FileResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib import messages
from django.db import transaction
from django.db.models import Q

from .models import IdSource, Identifier, Person, HEI, StudentCard
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
        source = request.session.get('authn_source', None)
        attribute = request.session.get('authn_attribute', None)
        if (person_id is None and
            otp is None and
            source is None and
            attribute is None):
            # Something smells fishy...
            if getattr(settings, 'DEBUG', False): print('auth. No nothing')
            request.session.flush()
            return HttpResponseForbidden(_('Access not permitted'))
        if person_id is None and otp is not None:
            # We have a token for a person
            # Get the person
            person = get_object_or_404(Person, otp=otp)
            # Signal that linking is required
            request.session['authn_phase'] = 'link'
        if person_id is not None and otp is None:
            # Get the person
            person = get_object_or_404(Person, pk=person_id)
            # Signal that the person is already known
            request.session['authn_phase'] = 'end'
        if person_id is not None and otp is not None:
            # We can link
            # Get the person with both attributes
            person = get_object_or_404(Person, pk=person_id, otp=otp)
            # Signal that linking is required
            request.session['authn_phase'] = 'link'
        if source is not None and attribute is not None and person_id is None:
            # We have an indirect identification
            source = IdSource.objects.filter(source=source).first()
            identifier = Identifier.objects.filter(source=source,
                                                   value=attribute).first()
            if identifier is None:
                if getattr(settings, 'DEBUG', False): print('No identifier')
                request.session.flush()
                return HttpResponseForbidden(_('Access not permitted'))
            person = identifier.person
        # Log the person in
        login(request, person)
        return redirect(request.session.get('next', reverse('esiidm:start')))
    # How did we get here? Someone is messing with the session ...
    if getattr(settings, 'DEBUG', False): print('auth. final')
    request.session.flush()
    return HttpResponseForbidden(_('Access not permitted'))


def accept(request, token, response=None):
    """
    This view initiates the consent process once someone receives
    an invitation as student or officer.
    """
    # Check is the otp is still valid
    signer = TimestampSigner()
    try:
        # We allow for an extra hour
        age = get_setting('INVITE_MAX_HOURS', 25)
        otp = signer.unsign(token, max_age=60*60*age)
    except SignatureExpired:
        # The token is expired, but is otherwise valid
        otp = signer.unsign(token)
        # The OTP should point to known person, if not, we just explode
        person = Person.objects.get(otp=otp)
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
        if getattr(settings, 'DEBUG', False): print('accept. bad signature')
        request.session.flush()
        return HttpResponseForbidden(_('Access not permitted'))
    request.session['otp'] = otp
    # The OTP allows us to get the relevant user,
    # but is not verified by a login process
    person = Person.objects.get(otp=otp)
    request.session['person'] = person.id
    if not request.user.is_authenticated:
       return redirect(f'{settings.LOGIN_URL}?next={request.path}') 
    # The user should be authenticated now
    phase = request.session.get('authn_phase', None)
    source = request.session.get('authn_source', None)
    attribute = request.session.get('authn_attribute', None)
    person = request.user
    if phase is None or source is None or attribute is None:
        # Someone is messing with the session ...
        if getattr(settings, 'DEBUG', False): print('accept. no phase, source, att')
        request.session.flush()
        return HttpResponseForbidden(_('Access not permitted'))
    if phase == 'link':
        # We know how the person has authenticated, we can inform about it
        idsource = get_object_or_404(IdSource, source=source)
        # We need to add an Identifier for the Person
        if response is None and not person.has_accepted:
            # The person has not consented yet
            return render(request, 'esiidm/consent.html', {'source': source,
                                                           'token': token})
        if response == 'Y' or person.has_accepted:
            # We need a new identifier
            identifier, new = Identifier.objects.get_or_create(source=idsource,
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
            return render(request, 'esiidm/not_consent.html')
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
    template = 'esiidm/index.html' if request.user.is_authenticated \
                                   else 'esiidm/unknown.html'
    return render(request, template)

@login_required
def reinvite(request):
    if not request.user.is_authenticated:
        return redirect(reverse('esiidm:start'))
    host = get_setting('MAIL_ORIGIN_DOMAIN',
                       request.get_host().split(':')[0])
    result = request.user.invite(manager=None, hei=None, host=host,
                                 subject=_('Link for adding a new autentication'),
                                 template='esiidm/reinvite.txt')
    if result:
        messages.success(request, _('Link sent to {0}').format(request.user.email))
        messages.warning(request, _('Your session has been closed.'))
        logout(request)
    else:
        message.error(request, _('Send link to {0} failed.').format(request.user.email))
    return redirect(reverse('esiidm:start'))

@login_required
def end(request):
    """
    Kills the session and logs the user out.
    """
    request.session.flush()
    logout(request)
    return redirect(reverse('esiidm:start'))

@login_required
def cards(request, hid, blank=False):
    """
    Generates a PDF with all the cards for the HEI the officer manages.
    """
    if not request.user.is_officer:
        return HttpResponseForbidden(_('Access not permitted'))
    if not hid in [h.id for h in request.user.HEIs]:
        return HttpResponseForbidden(_('Access not permitted.'))
    hei = HEI.objects.get(id=hid)
    response = HttpResponse(hei.pdf_cards(blank),
                            content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={hei.sho}.cards.pdf'
    return response

@login_required
def statistics(request):
    """
    Generatest statistics for sharing with the EC
    """
    if not request.user.is_officer and not request.user.is_superuser:
        return HttpResponseForbidden(_('Access not permitted'))
    heis = []
    heicount = None
    cardcount = None

    if request.user.is_superuser or request.user.groups.filter(name='Stats').exists():
        heicount = HEI.objects.count()
        cardcount = StudentCard.objects.count()
        heis = HEI.objects.all()
    elif request.user.is_officer:
        heis = request.user.HEIs
    return render(request, 'esiidm/statistics.html',
                  {'heis': heis, 'heicount': heicount, 'cardcount': cardcount})
