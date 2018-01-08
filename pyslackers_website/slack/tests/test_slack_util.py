import pook
import pytest
from requests.exceptions import HTTPError

from pyslackers_website.slack.util import (
    SlackException,
    SlackClient,
)


class TestSlackClient:
    @pook.post('https://slack.com/api/users.admin.invite', reply=400)
    def test_invite_raises_on_bad_response(self, slack_client: SlackClient):
        with pytest.raises(HTTPError):
            slack_client.invite('foo@gmail.com', [])
        assert pook.isdone()

    @pook.post('https://slack.com/api/users.admin.invite', reply=200,
               response_json=dict(ok=False, error='already_invited'))
    def test_invite_raises_on_not_ok(self, slack_client: SlackClient):
        with pytest.raises(SlackException):
            slack_client.invite('foo@gmail.com', [])
        assert pook.isdone()

    @pook.post('https://slack.com/api/users.admin.invite', reply=200,
               response_json=dict(ok=True))
    def test_invite_returns_true_on_ok(self, slack_client: SlackClient):
        assert slack_client.invite('foo@gmail.com', [])
        assert pook.isdone()

    @pook.get('https://slack.com/api/users.list', reply=400)
    def test_members_raises_on_bad_response(self, slack_client: SlackClient):
        with pytest.raises(HTTPError):
            slack_client.members()
        assert pook.isdone()

    @pook.get('https://slack.com/api/users.list', reply=200,
              response_json=dict(ok=False, error='something'))
    def test_members_raises_on_not_ok(self, slack_client: SlackClient):
        with pytest.raises(SlackException):
            slack_client.members()
        assert pook.isdone()

    @pook.get('https://slack.com/api/users.list', reply=200,
              response_json=dict(ok=True, members=[]))
    def test_members_list_on_ok(self, slack_client: SlackClient):
        assert isinstance(slack_client.members(), list)
        assert pook.isdone()

    @pook.get('https://slack.com/api/channels.list', reply=400)
    def test_channels_raises_on_bad_response(self, slack_client: SlackClient):
        with pytest.raises(HTTPError):
            slack_client.channels()
        assert pook.isdone()

    @pook.get('https://slack.com/api/channels.list', reply=200,
              response_json=dict(ok=False, error='something'))
    def test_channels_raises_on_not_ok(self, slack_client: SlackClient):
        with pytest.raises(SlackException):
            slack_client.channels()
        assert pook.isdone()

    @pook.get('https://slack.com/api/channels.list', reply=200,
              response_json=dict(ok=True, channels=[]))
    def test_channels_list_on_ok(self, slack_client: SlackClient):
        assert isinstance(slack_client.channels(), list)
        assert pook.isdone()
