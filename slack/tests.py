# from unittest import mock

from django.test import TestCase

from marketing.models import BurnerDomain
from .forms import SlackInviteForm
# from .tasks import send_slack_invite


class TestSlackInviteForm(TestCase):
    """Tests to validate that the slack invite form runs
    the appropriate validations"""

    def test_blank_data(self):
        form = SlackInviteForm({})
        self.assertFalse(form.is_valid())
        # don't really care about the message text so much
        self.assertEqual(set(form.errors.keys()),
                         {'email', 'accept_tos'})

    def test_allows_non_burner_domain(self):
        form = SlackInviteForm({
            'email': 'foo@bar.com',
            'accept_tos': True,
        })
        self.assertTrue(form.is_valid())

    def test_invalidates_burner_domain(self):
        BurnerDomain.objects.create(domain='bar.com')
        form = SlackInviteForm({
            'email': 'foo@bar.com',
            'accept_tos': True,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'email': ['Email is from a suspected burner domain'],
        })
