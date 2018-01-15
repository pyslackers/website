import re

from django.db.models import Value, F, Func
from django.forms import ValidationError
from django.utils.translation import gettext as _

from .models import Invite


def validate_not_duplicate_email(email: str):
    """Validate that the email has not already received an
    invite from us. In the rare case someone needs a second
    we can manually do it for now via our email."""
    username, domain = email.split('@')
    stripped_username = re.sub(r'(?:\.|\+.*$)', '', username)
    matching_invites = Invite.objects.filter(
        email__iendswith=f'@{domain}', blocked=True)\
        .annotate(username=Func(F('email'), Value('(\.|\+.*$|@.*$)'),
                                Value(''), Value('g'),
                                function='regexp_replace'))\
        .filter(username__iexact=stripped_username)
    if matching_invites.exists():
        raise ValidationError(_('Email appears to be a duplicate, please '
                                'email us if that is incorrect.'))
