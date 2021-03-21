# -*- coding: utf-8 -*-
# vim:ts=4:expandtab:ai
# $Id$

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.signing import TimestampSigner
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as pgettext
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q

from .models import HEI, Person, Officer, StudentCard
from .forms import loadCards

def login(request):
    """
    This view logs the user in, using data in the session that
    has been loaded by one of the authentication modules.
    """

