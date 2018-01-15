from django import forms

from app.marketing.validators import validate_not_burner_domain
from .validators import validate_not_duplicate_email


class SlackInviteForm(forms.Form):
    """Form for slack invitation requests"""
    email = forms.EmailField(validators=[
        validate_not_burner_domain,
        validate_not_duplicate_email,
    ])
    accept_tos = forms.BooleanField()
