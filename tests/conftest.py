from unittest.mock import MagicMock, AsyncMock
import pytest

import pyslackersweb
from pyslackersweb.sirbot.models import codewars
import pyslackersweb.website.tasks

from sqlalchemy import delete


class SlackClient:
    def __init__(self):
        self.api = MagicMock()
        self._request = MagicMock(return_value={"ok": True})
        self._request._mock_awaited = False
        self._request.side_effect = None

        # Use AsyncMock for query which properly handles async calls
        self.query = AsyncMock(return_value={"ok": True})
        self.query._mock_awaited = False

    async def invite(self, email: str, domain: str):
        return {"ok": True}

    async def iter(self, url: str, minimum_time: int = 0):
        import slack.methods

        if url == slack.methods.CONVERSATIONS_LIST:
            # Yield channel data for sync_slack_channels
            data = [
                {
                    "id": "C0123456789",
                    "name": "general",
                    "created": 1234567890,
                    "is_archived": False,
                    "num_members": 42,
                    "topic": {"value": "General discussion"},
                    "purpose": {"value": "This is the general channel"},
                }
            ]
        else:
            # Yield user data for sync_slack_users (existing behavior)
            data = [
                {
                    "id": "U0123456789",
                    "deleted": False,
                    "is_admin": False,
                    "is_bot": False,
                    "tz": "America/New_York",
                }
            ]

        # Yield each item to create an async iterator
        for item in data:
            yield item

    def reset_mock(self):
        self.query.reset_mock()
        self.query.return_value = {"ok": True}
        self.query.side_effect = None
        self._request.reset_mock()
        self._request.return_value = {"ok": True}
        self._request.side_effect = None

    def success(self, return_value=None):
        self.query.side_effect = None
        self.query.return_value = return_value or {"ok": True}
        return self

    def api_error(self, error, data=None):
        import slack.exceptions

        self.query.side_effect = slack.exceptions.SlackAPIError(
            error=error, headers={}, data=data or {"ok": False, "error": error}
        )
        return self

    def http_error(self, status=500):
        import slack.exceptions

        self.query.side_effect = slack.exceptions.HTTPException(
            status=status, headers={}, data={"error": "Error contacting slack API"}
        )
        return self

    def should_not_be_called(self, message="Slack client should not be called"):
        self.query.side_effect = AssertionError(message)
        return self


@pytest.fixture
async def slack_client():
    client = SlackClient()
    yield client
    client.reset_mock()


@pytest.fixture()
async def slack_client_ctx(slack_client):
    async def ctx(app):
        pyslackersweb.contexts._register_in_app(app, "slack_client", slack_client)
        pyslackersweb.contexts._register_in_app(app, "slack_client_legacy", slack_client)
        yield

    return ctx


@pytest.fixture
async def client(monkeypatch, aiohttp_client, slack_client_ctx):

    # Patch imported slack_client context in pyslackersweb/__init__.py with the fake slack client ctx
    monkeypatch.setattr(pyslackersweb, "slack_client", slack_client_ctx)

    application = await pyslackersweb.app_factory()

    app_client = await aiohttp_client(application)
    app_client.app["scheduler"].shutdown()

    yield app_client

    # cleanup database
    async with app_client.app["pg"].acquire() as conn:
        await conn.fetch(delete(pyslackersweb.models.domains))
        await conn.fetch(delete(pyslackersweb.models.SlackUsers))
        await conn.fetch(delete(pyslackersweb.models.SlackChannels))
        await conn.fetch(delete(codewars))


@pytest.fixture
def slack_mock(client):
    """Convenient fixture to access and configure the slack client mock"""
    return client.app["slack_client_legacy"]
