import logging

from collections import namedtuple

import pytest
import aiohttp.web
from sqlalchemy.dialects.postgresql import insert as pg_insert

from pyslackersweb.website import tasks
from pyslackersweb.models import Source, domains

SlackInviteTestParam = namedtuple("Param", "response data expected")


async def test_endpoint_index(client):
    r = await client.get("/")

    assert r.history[0].url.path == "/"
    assert r.history[0].status == 302

    assert r.status == 200
    assert r.url.path == "/web"


async def test_endpoint_slack(client):
    r = await client.get("/web/slack")
    assert r.status == 200


@pytest.mark.parametrize(
    "slack_client,data,expected",
    (
        SlackInviteTestParam(
            response={},
            data={"email": "error@example.com", "agree_tos": True},
            expected="successAlert",
        ),
        SlackInviteTestParam(
            response={}, data={"agree_tos": True}, expected="Missing data for required field"
        ),
        SlackInviteTestParam(
            response={},
            data={"email": "error@example.com", "agree_tos": False},
            expected="There was an error processing your invite",
        ),
        SlackInviteTestParam(
            response={},
            data={"email": "foobar", "agree_tos": True},
            expected="Not a valid email address",
        ),
        SlackInviteTestParam(
            response={"body": {"ok": False, "error": "already_in_team"}},
            data={"email": "error@example.com", "agree_tos": True},
            expected="Reason: already_in_team",
        ),
        SlackInviteTestParam(
            response={"body": {"ok": False, "error": "not_authed"}},
            data={"email": "error@example.com", "agree_tos": True},
            expected="Reason: not_authed",
        ),
        SlackInviteTestParam(
            response={"status": 500},
            data={"email": "error@example.com", "agree_tos": True},
            expected="Reason: Error contacting slack API",
        ),
    ),
    indirect=["slack_client"],
)
async def test_endpoint_slack_invite(client, data, expected):
    r = await client.post(path="/web/slack", data=data)
    html = await r.text()

    assert r.status == 200
    assert expected in html


@pytest.mark.parametrize(
    "slack_client,data,expected",
    (
        SlackInviteTestParam(
            response={}, data={"email": "foo@urhen.com", "agree_tos": True}, expected="successAlert"
        ),
    ),
    indirect=["slack_client"],
)
async def test_invite_banned_email_domain(client, data, expected):
    async with client.app["pg"].acquire() as conn:
        await conn.fetchrow(
            pg_insert(domains)
            .values(domain="urhen.com", blocked=True, source=Source.MANUAL)
            .on_conflict_do_nothing(index_elements=[domains.c.domain])
        )
    r = await client.post(path="/web/slack", data=data)
    html = await r.text()

    assert r.status == 200
    assert expected in html
    client.app["subapps"]["website"][  # pylint: disable=protected-access
        "slack_client"
    ]._request.assert_not_awaited()


@pytest.fixture
def disable_invites():
    import pyslackersweb.website.settings

    pyslackersweb.website.settings.DISABLE_INVITES = True

    yield

    pyslackersweb.website.settings.DISABLE_INVITES = False


async def test_disable_invites(client, disable_invites):
    r = await client.get(path="/web/slack")
    html = await r.text()

    assert r.status == 200
    assert "Invites are disabled at this time" in html

    r = await client.post(path="/web/slack", data={"email": "foo@example.com", "agree_tos": True})
    html = await r.text()

    assert r.status == 200
    assert "Invites are disabled at this time" in html
    assert not client.app["slack_client"]._request.called


async def test_task_sync_github_repositories(client, caplog):

    async with aiohttp.ClientSession() as session:
        result = await tasks.sync_github_repositories(session, client.app["redis"])

    assert result

    for record in caplog.records:
        assert record.levelno <= logging.INFO


@pytest.mark.parametrize("slack_client", ({"body": ["users_iter", "users"]},), indirect=True)
async def test_task_sync_slack_users(client, caplog):

    result = await tasks.sync_slack_users(client.app["slack_client"], client.app["redis"])

    assert result
    assert len(result) == 1
    assert result["America/Los_Angeles"] == 2

    for record in caplog.records:
        assert record.levelno <= logging.INFO


@pytest.mark.parametrize("slack_client", ({"body": ["channels_iter", "channels"]},), indirect=True)
async def test_task_sync_slack_channels(client, caplog):

    result = await tasks.sync_slack_channels(client.app["slack_client"], client.app["redis"])

    assert result

    for record in caplog.records:
        assert record.levelno <= logging.INFO
