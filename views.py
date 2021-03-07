# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.core.signing import TimestampSigner
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as pgettext
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

from .models import HEI, Person, Officer, StudentCard

def login(request):
    """
    This view logs the user in, using data in the session that has been loaded by
    one of the authentication modules.
    """

@login_required
def load(request):
    """
    Basic view for finding out the type of objects that the user is
    allowed to upload.
    It does either of two actions:
        - Redirect to the form for uploading cards (with student data),
          for officers.
        - Offer a list of options for superusers and helpers.
    """
    # Only staff allowed here
    if not request.user.is_staff: return HttpResponseForbidden
    # Officers can load only cards
    if request.user.is_officer:
        return redirect(reverse('esiidm:loadCards')
    # Offer options to the other staff members
    return render(request, 'esiidm/load.html')

