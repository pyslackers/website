from unittest import mock

from django.test import TestCase

from .models import BurnerDomain
from .tasks import send_slack_invite


class TestSlackInviteTask(TestCase):
    def setUp(self):
        BurnerDomain.objects.create(domain='foo.com')

    @mock.patch('requests.Session.post')
    def test_sends_to_non_burners(self, mocked_post):
        send_slack_invite('foo@gmail.com')
        self.assertTrue(mocked_post.called)

    @mock.patch('requests.Session.post')
    def test_ignores_burner_domains(self, mocked_post):
        send_slack_invite('foo@foo.com')
        self.assertFalse(mocked_post.called)
