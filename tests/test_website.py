import logging

import pytest
import aiohttp.web
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from pyslackersweb.website import tasks
from pyslackersweb.models import Source, domains


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
    "data,expected",
    [
        pytest.param(
            {"email": "error@example.com", "agree_tos": True},
            {"html": "successAlert", "domain": "example.com", "status": 200},
            id="valid_email_lowercase",
        ),
        pytest.param(
            {"email": "error@EXAMPLE.COM", "agree_tos": True},
            {"html": "successAlert", "domain": "example.com", "status": 200},
            id="valid_email_uppercase",
        ),
    ],
)
async def test_endpoint_slack_invite_success(client, slack_mock, data, expected):
    slack_mock.success()

    r = await client.post("/web/slack", data=data)
    html = await r.text()

    assert r.status == expected["status"]
    assert "successAlert" in html
    assert "See you in Slack!" in html
    assert "Check your inbox" in html

    if "domain" in expected:
        async with client.app["pg"].acquire() as conn:
            rows = await conn.fetch(select([domains.c.blocked, domains.c.domain]))

        assert len(rows) == 1
        assert rows[0]["domain"] == expected["domain"]


@pytest.mark.parametrize(
    "data,expected",
    [
        pytest.param(
            {"agree_tos": True},
            {"html": "errorAlert", "status": 200},
            id="missing_email",
        ),
        pytest.param(
            {"email": "error@example.com", "agree_tos": False},
            {"html": "errorAlert", "status": 200},
            id="agree_tos_false",
        ),
        pytest.param(
            {"email": "foobar", "agree_tos": True},
            {"html": "errorAlert", "status": 200},
            id="invalid_email_format",
        ),
    ],
)
async def test_endpoint_slack_invite_validation_errors(client, data, expected):
    r = await client.post("/web/slack", data=data)
    html = await r.text()

    assert r.status == expected["status"]
    assert "errorAlert" in html
    assert "Could you check something?" in html
    assert "There was an error processing your invite" in html


@pytest.mark.parametrize(
    "data,expected",
    [
        pytest.param(
            {"email": "error@example.com", "agree_tos": True},
            {
                "html": "errorAlert",
                "domain": "example.com",
                "status": 200,
                "response": {"body": {"ok": False, "error": "already_in_team"}},
            },
            id="already_in_team",
        ),
        pytest.param(
            {"email": "error@example.com", "agree_tos": True},
            {
                "html": "errorAlert",
                "domain": "example.com",
                "status": 200,
                "response": {"body": {"ok": False, "error": "already_invited"}},
            },
            id="already_invited",
        ),
        pytest.param(
            {"email": "error@example.com", "agree_tos": True},
            {
                "html": "errorAlert",
                "domain": "example.com",
                "status": 200,
                "response": {"body": {"ok": False, "error": "not_authed"}},
            },
            id="not_authenticated",
        ),
        pytest.param(
            {"email": "error@example.com", "agree_tos": True},
            {
                "html": "errorAlert",
                "domain": "example.com",
                "status": 200,
                "response": {"status": 500},
            },
            id="http_exception",
        ),
    ],
)
async def test_endpoint_slack_invite_failure(client, slack_mock, data, expected):
    if "response" in expected:
        if "body" in expected["response"]:
            error = expected["response"]["body"]["error"]
            slack_mock.api_error(error, expected["response"]["body"])
        elif "status" in expected["response"]:
            slack_mock.http_error(expected["response"]["status"])

    r = await client.post(path="/web/slack", data=data)
    html = await r.text()

    assert r.status == expected["status"]
    assert "errorAlert" in html

    if "response" in expected and "body" in expected["response"]:
        assert expected["response"]["body"]["error"] in html
    elif "response" in expected and "status" in expected["response"]:
        assert "Could you check something?" in html
        assert "There was an error processing your invite" in html
        assert "Reason: Error contacting slack API" in html

    if "domain" in expected:
        async with client.app["pg"].acquire() as conn:
            rows = await conn.fetch(select([domains.c.blocked, domains.c.domain]))

        assert len(rows) == 1
        assert rows[0]["domain"] == expected["domain"]


@pytest.mark.parametrize(
    "data,expected",
    [
        pytest.param(
            {"email": "test@urhen.com", "agree_tos": True},
            "This email domain is not allowed",
            id="banned_domain_basic",
        ),
        pytest.param(
            {"email": "test@urhen.com", "agree_tos": True, "first_name": "Test"},
            "This email domain is not allowed",
            id="banned_domain_with_first_name",
        ),
        pytest.param(
            {"email": "test@urhen.com", "agree_tos": True, "last_name": "User"},
            "This email domain is not allowed",
            id="banned_domain_with_last_name",
        ),
        pytest.param(
            {
                "email": "test@urhen.com",
                "agree_tos": True,
                "first_name": "Test",
                "last_name": "User",
            },
            "This email domain is not allowed",
            id="banned_domain_with_full_name",
        ),
    ],
)
async def test_invite_banned_email_domain(client, slack_mock, data, expected):
    slack_mock.should_not_be_called("Slack client query should not be called for banned domains")

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
    client.app["slack_client_legacy"].query.assert_not_called()


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
    client.app["slack_client_legacy"].query.assert_not_called()


async def test_invite_use_legacy_client(client):
    data = {"email": "error@example.com", "agree_tos": True}

    # First call should work fine with mock client
    r = await client.post(path="/web/slack", data=data)
    assert r.status == 200

    # Remove the slack client to test error handling
    # Need to remove from both root and subapp since they might have separate copies
    if "slack_client_legacy" in client.app:
        del client.app["slack_client_legacy"]
    if "subapps" in client.app and "website" in client.app["subapps"]:
        if "slack_client_legacy" in client.app["subapps"]["website"]:
            del client.app["subapps"]["website"]["slack_client_legacy"]

    r = await client.post(path="/web/slack", data=data)
    assert r.status == 500


async def test_task_sync_github_repositories(client, caplog):
    async with aiohttp.ClientSession() as session:
        result = await tasks.sync_github_repositories(session, client.app["redis"])

    assert result

    for record in caplog.records:
        assert record.levelno <= logging.INFO


@pytest.mark.parametrize(
    "data,expected",
    [
        pytest.param(
            {"email": "test@example.com", "agree_tos": True},
            "successAlert",
            id="success_lowercase_email",
        ),
        pytest.param(
            {"email": "test@EXAMPLE.com", "agree_tos": True},
            "successAlert",
            id="success_uppercase_email",
        ),
    ],
)
async def test_invite_success(client, slack_mock, data, expected):
    r = await client.post(path="/web/slack", data=data)
    html = await r.text()

    assert r.status == 200
    assert expected in html
    client.app["slack_client_legacy"].query.assert_called_once()
