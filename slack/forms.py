import logging

from django import forms

from marketing.models import BurnerDomain

logger = logging.getLogger('pyslackers.slack.forms')


class SlackInviteForm(forms.Form):
    """Form for slack invitation requests"""
    email = forms.EmailField()
    accept_tos = forms.BooleanField()
    # additional_channels = forms.MultiValueField(required=False)

    def clean_email(self):
        email = self.cleaned_data['email']
        if BurnerDomain.is_burner(email):
            raise forms.ValidationError('Email is from a suspected burner '
                                        'domain')
        return email
