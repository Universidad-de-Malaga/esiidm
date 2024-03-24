# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.signing import TimestampSigner
from django.core.signing import SignatureExpired
from django.core.signing import BadSignature
from django.db import transaction
from django.db.models import Q
from django.http import FileResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as pgettext
from django.views import View
from django.views.decorators.csrf import csrf_exempt

import base64
import json

from .models import IdSource, Identifier, Person, HEI, StudentCard, AuthLog
from .utils import get_setting


def authenticate(request):
    """
    This view logs the user in, using data in the session that
    has been loaded by one of the authentication modules.
    """
    # We keep the step that started the login flow in the session
    if request.session.get('next', None) is None:
        request.session['next'] = request.GET.get(
            'next', reverse('esiidm:start')
        )
    phase = request.session.get('authn_phase', None)
    if phase is None:
        # Signal we are starting the login process
        request.session['authn_phase'] = 'start'
        # Get active authentication sources
        sources = IdSource.objects.filter(active=True)
        return render(
            request, 'esiidm/auth_sources.html', {'sources': sources}
        )
    if phase == 'login':
        # We are back from an authentication source
        # The session may contain either a token or the id for the person
        person_id = request.session.get('person', None)
        otp = request.session.get('otp', None)
        source = request.session.get('authn_source', None)
        attribute = request.session.get('authn_attribute', None)
        if (
            person_id is None
            and otp is None
            and source is None
            and attribute is None
        ):
            # Something smells fishy...
            if getattr(settings, 'DEBUG', False):
                print('auth. No nothing')
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
            identifier = Identifier.objects.filter(
                source=source, value=attribute
            ).first()
            if identifier is None:
                if getattr(settings, 'DEBUG', False):
                    print('No identifier')
                request.session.flush()
                return HttpResponseForbidden(_('Access not permitted'))
            person = identifier.person
        # Log the person in
        go_to = request.session.get('next', reverse('esiidm:start'))
        login(request, person)
        # Log the authentication
        how = source
        if type(source) == str:
            how = IdSource.objects.get(source=source)
        AuthLog(hei=person.myHEI, how=how, what=go_to[:50]).save()
        return redirect(go_to)
    # How did we get here? Someone is messing with the session ...
    if getattr(settings, 'DEBUG', False):
        print('auth. final')
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
        otp = signer.unsign(token, max_age=60 * 60 * age)
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
        host = get_setting(
            'MAIL_ORIGIN_DOMAIN', request.get_host().split(':')[0]
        )
        result = person.invite(
            person.managedBy, hei=hei, host=host, template=template
        )
        return render(request, 'esiidm/expired.html', {'sent': result})
    except BadSignature:
        if getattr(settings, 'DEBUG', False):
            print('accept. bad signature')
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
        if getattr(settings, 'DEBUG', False):
            print('accept. no phase, source, att')
        request.session.flush()
        return HttpResponseForbidden(_('Access not permitted'))
    if phase == 'link':
        # We know how the person has authenticated, we can inform about it
        idsource = get_object_or_404(IdSource, source=source)
        # We need to add an Identifier for the Person
        if response is None and not person.has_accepted:
            # The person has not consented yet
            return render(
                request,
                'esiidm/consent.html',
                {'source': source, 'token': token},
            )
        if response == 'Y' or person.has_accepted:
            # We need a new identifier
            identifier, new = Identifier.objects.get_or_create(
                source=idsource, person=person, value=attribute
            )
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
    template = (
        'esiidm/index.html'
        if request.user.is_authenticated
        else 'esiidm/unknown.html'
    )
    return render(request, template)


@login_required
def reinvite(request):
    if not request.user.is_authenticated:
        return redirect(reverse('esiidm:start'))
    host = get_setting('MAIL_ORIGIN_DOMAIN', request.get_host().split(':')[0])
    result = request.user.invite(
        manager=None,
        hei=None,
        host=host,
        subject=_('Link for adding a new autentication'),
        template='esiidm/reinvite.txt',
    )
    if result:
        messages.success(
            request, _('Link sent to {0}').format(request.user.email)
        )
        messages.warning(request, _('Your session has been closed.'))
        logout(request)
    else:
        message.error(
            request, _('Send link to {0} failed.').format(request.user.email)
        )
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
    response = HttpResponse(
        hei.pdf_cards(blank), content_type='application/pdf'
    )
    response[
        'Content-Disposition'
    ] = f'attachment; filename={hei.sho}.cards.pdf'
    return response


@login_required
def statistics(request):
    """
    Generatest statistics for sharing with the EC
    """
    heis = []
    heicount = None
    cardcount = None
    authcount = None

    if (
        request.user.is_superuser
        or request.user.groups.filter(name='Stats').exists()
    ):
        heicount = HEI.objects.count()
        cardcount = StudentCard.objects.count()
        authcount = AuthLog.objects.count()
        heis = HEI.objects.all()
    elif request.user.is_officer:
        heis = request.user.HEIs
    else:
        return HttpResponseForbidden(_('Access not permitted'))
    return render(
        request,
        'esiidm/statistics.html',
        {
            'heis': heis,
            'heicount': heicount,
            'cardcount': cardcount,
            'authcount': authcount,
        },
    )


# API implementation for direct student and card creation
# There is no human interaction, so, no browser cookies
@method_decorator(csrf_exempt, name='dispatch')
class TheAPI(View):
    """
    The class methods implement RESTful operations on objects:
    Students and their Cards (StudentCards and their owning Persons).
        + GET mainly for obtaining a deletion token
        + DELETE for deleting objects
        + PUT for adding objets
    For the API to work, the HEI needs to have a special "officer" named "API
    Officer" (first_name=API, last_name=Officer) whose email is the assigned
    API key @ the SHO of the corresponding HEI like key@sho, such key MUST be
    sent in an Authorization header.
    """

    hei = None
    officer = None
    host = None

    def dispatch(self, request, *args, **kwargs):
        """
        Obtains the HEI that has a given SHO.
        Obtains the API officer for the corresponding HEI with the given
        authtoken.
        If the objects cannot be retrieved, the action is not authorised.
        """
        self.host = request.get_host().split(':')[0]
        hei = HEI.objects.filter(sho=sho)
        if not len(hei) == 1:
            return HttpResponseForbidden
        self.hei = hei[0]
        token = request.headers.get('Authorization', None)
        if token is None:
            return HttpResponseForbidden
        officer = Officer.objects.filter(
            hei=self.hei, person__email=f'{token}@{sho}'
        )
        if not len(officer) == 1:
            return HttpResponseForbidden
        self.officer = officer[0]
        return super().dispatch(request, args, kwargs)

    def put(self, request, *args, **kwargs):
        """
        We use the PUT method for adding StudentCards via API like the
        batches do.
        We expect a JSON structure containing a list of 0 to N dictionaries
        that we can pass to the loading logic used in the admin.
        Each dictionary MUST be numbered starting from 1 for error
        referential pourposes, like:
        [
          {
            "number": 1,
            "esi": "0612345678",
            "first_name": "Bianca",
            "last_name": "Castafiore"
          }
        ]
        An element called "identifier" with a legal person identifier like
        Goverment ID or passport number MAY be present.
        Operation, if present, will be changed to C, PUT method MUST NOT delete
        objects.
        """
        lines = json.loads(request.body.decode('utf-8'))
        total, cards, deleted, new_persons, new_cards, errors = process_lines(
            lines, self.hei, self.officer, self.host, False
        )
        response_data = {}
        messages = []
        # Reporting...
        if not total == 0:
            if not new_persons == 0:
                messages.append(f'{new_persons} persons added.')
            if not new_cards == 0 or not new_persons == 0:
                # Cards are added for existing and new persons
                messages.append(f'{new_cards + new_persons} cards added.')
        response_data['message'] = ' '.join(messages)
        status = 201
        if not len(errors) == 0:
            status = 409
            response_data['message'] = ' '.join(errors)
        return JsonResponse(response_data, status=status)

    def get(self, request, *args, **kwargs):
        """
        Receives an ESI that belongs to a given HEI.
        Returns the data with a signed token that has to be sent for deletion.
        """
        response_data = {}
        status = 201
        card = StudentCard.objects.filter(hei=self.hei, esi=esi)
        if not len(card) == 1:
            status = 409
            response_data[
                'message'
            ] = f'ESI {esi} for HEI {self.hei.sho} not found'
        else:
            card = card[0]
            response_data['esi'] = card.esi
            response_data['esc'] = card.esc
            response_data['first_name'] = card.student.first_name
            response_data['last_name'] = card.student.last_name
            signer = TimestampSigner()
            token = {'esi': card.esi, 'esc': card.esc, 'otp': card.student.otp}
            response_data['delcode']: signer.sign(
                base64.b64encode(json.dumps(token), 'ascii')
            )
        return JsonResponse(response_data, status=status)

    def delete(self, request, *args, **kwargs):
        """
        Receives a HEI, an ESI and a signed token for finding the card.
        Deletes the StudentCard with its side effects.
        Status 204 to be consistent with the ESC Router API.
        """
        # Check is the otp is still valid
        signer = TimestampSigner()
        try:
            # We allow for a five minutes delay from GET
            age = get_setting('API_MAX_MIN', 5)
            token = signer.unsign(delcode, max_age=60 * age)
        except SignatureExpired:
            return HttpResponseForbidden(
                'Access not permitted. Expired token.'
            )
        except BadSignature:
            return HttpResponseForbidden(
                'Access not permitted. Invalid token.'
            )
        token = json.loads(base64.b64decode(token))
        # Security verification, we are deleting, intentions double check
        if not esi == token['esi']:
            return HttpResponseForbidden(
                'Access not permitted. Invalid token.'
            )
        card = StudentCard.objects.filter(
            hei=hei,
            esi=token['esi'],
            esc=token['esc'],
            student__otp=token['otp'],
        )
        if not len(card) == 1:
            status = 409
            response_data[
                'message'
            ] = f'ESI {esi} for HEI {self.hei.sho} not found'
        else:
            card[0].delete()
        response_data = {}
        return JsonResponse(response_data, status=204)
