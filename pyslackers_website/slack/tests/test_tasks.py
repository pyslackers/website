import uuid
from mock import Mock

import pook
import pytest

from pyslackers_website.slack.models import Membership
from pyslackers_website.slack.tasks import (
    send_slack_invite,
    capture_snapshot_of_user_count
)


class TestSendSlackInvite:
    def test_defaults_channels(self, settings, monkeypatch):
        mock_slack_client = Mock()
        settings.SLACK_JOIN_CHANNELS = ['foo', 'bar']
        settings.SLACK_OAUTH_TOKEN = str(uuid.uuid4())
        monkeypatch.setattr('pyslackers_website.slack.tasks.SlackClient',
                            mock_slack_client)

        send_slack_invite('foobar@example.com')
        mock_slack_client.assert_called_with(settings.SLACK_OAUTH_TOKEN)
        (mock_slack_client.return_value.invite
            .assert_called_with('foobar@example.com',
                                ['foo', 'bar'],
                                resend=True))

    def test_override_channels(self, settings, monkeypatch):
        mock_slack_client = Mock()
        settings.SLACK_JOIN_CHANNELS = ['foo', 'bar']
        settings.SLACK_OAUTH_TOKEN = str(uuid.uuid4())
        monkeypatch.setattr('pyslackers_website.slack.tasks.SlackClient',
                            mock_slack_client)

        send_slack_invite('foobar@example.com',
                          channels=['baz'], resend=False)
        mock_slack_client.assert_called_with(settings.SLACK_OAUTH_TOKEN)
        (mock_slack_client.return_value.invite
            .assert_called_with('foobar@example.com',
                                ['baz'], resend=False))


class TestCaptureSnapshotOfUserCount:
    @pook.get('https://slack.com/api/users.list',
              response_json={
                  'ok': True,
                  'members': [
                      {'is_bot': True, 'deleted': False},
                      {'is_bot': True, 'deleted': False},
                      {'is_bot': True, 'deleted': False},
                      {'deleted': True},
                      {'tz': 'America/Denver'},
                      {'tz': 'Europe/London'},
                      {'tz': 'Europe/London'},
                      {'tz': 'America/Denver'},
                      {'tz': 'America/Denver'},
                  ]
              })
    @pytest.mark.django_db
    def test_captures_snapshot(self):
        capture_snapshot_of_user_count()
        mem = Membership.objects.latest()
        assert mem.member_count == 5
        assert mem.deleted_count == 1
        assert mem.bot_count == 3
        assert mem.tz_count_json == {
            'America/Denver': 3,
            'Europe/London': 2,
        }
