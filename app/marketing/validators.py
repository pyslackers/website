from django.forms import ValidationError
from django.utils.translation import gettext as _

from .models import BurnerDomain


def validate_not_burner_domain(email: str):
    """Validate that the provided email is not considered a "burner"
    domain, e.g. someone not interested in committing and contributing to
    the community or the ability to recover their account."""
    email, domain = email.split('@')
    try:
        BurnerDomain.objects.get(domain__iexact=domain)
        raise ValidationError(_('%(value)s is a suspected throw-away domain'),
                              params={'value': domain})
    except BurnerDomain.DoesNotExist:
        pass
