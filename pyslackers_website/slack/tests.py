# from unittest import mock

from django.core.cache import cache
from django.test import RequestFactory, TestCase

from pyslackers_website.marketing.models import BurnerDomain
from .forms import SlackInviteForm
from .views import SlackInvite

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


class TestSlackInviteView(TestCase):
    """ Test case for Slack invite and map page """

    def setUp(self):
        self.factory = RequestFactory()
        self.slack_member_tz_count = (('TestArea', 5), ('TestArea2', 2))

    def test_no_user_count(self):
        """ Assert slack member data is properly set without celery invocation """
        request = self.factory.get('/slack/')
        response = SlackInvite.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['slack_member_count'], 0)
        self.assertEqual(response.context_data['slack_member_tz_count'], [])

    def test_user_count_and_tz_count_from_cache(self):
        """ Assert slack member data is properly being pulled from cache """
        cache.set('slack_member_count', 7)
        cache.set('slack_member_tz_count', self.slack_member_tz_count)
        request = self.factory.get('/slack/')
        response = SlackInvite.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['slack_member_count'], 7)
        self.assertEqual(response.context_data['slack_member_tz_count'],
                         self.slack_member_tz_count)
