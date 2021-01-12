import json
import pytest
import json

from unittest import mock
from slack import methods

from pyslackersweb.sirbot import settings, tasks, models
from sqlalchemy.dialects.postgresql import insert as pg_insert


@pytest.mark.parametrize(
    "payload,expected",
    (
        (
            {
                "name": "pyslackers/website",
                "build": {"commit": "abcdefghijkl", "state": "finished", "success": True},
            },
            {"status": "successful", "project": "pyslackers/website@abcdefg"},
        ),
        (
            {
                "name": "pyslackers/slack-sansio",
                "build": {"commit": "1234567890", "state": "finished", "success": False},
            },
            {"status": "failed", "project": "pyslackers/slack-sansio@1234567"},
        ),
        (
            {
                "name": "pyslackers/slack-sansio",
                "build": {"commit": None, "state": "triggered", "success": True},
            },
            None,
        ),
    ),
)
async def test_readthedocs_notification(client, payload, expected):
    r = await client.post("/bot/readthedocs", json=payload)
    assert r.status == 200

    mocked_request = client.app["slack_client"]._request
    if not expected:
        # Assert we do not send a message to slack
        mocked_request.assert_not_called()
        return

    # Assert we send a message to slack
    mocked_request.assert_called_once()
    mocked_request_args = mocked_request.call_args.args

    assert methods.CHAT_POST_MESSAGE.value[0] in mocked_request_args
    assert settings.READTHEDOCS_NOTIFICATION_CHANNEL in mocked_request_args[3]
    assert expected["project"] in mocked_request_args[3]
    assert expected["status"] in mocked_request_args[3]


async def test_readthedocs_notification_missing_name(client):
    r = await client.post("/bot/readthedocs", json={})
    assert r.status == 400

    # Assert we did not send a message to slack
    assert not client.app["slack_client"]._request.called


async def test_task_codewars_challenge(client, caplog):
    await tasks.post_slack_codewars_challenge(client.app["slack_client"], client.app["pg"])

    mocked_request = client.app["slack_client"]._request
    mocked_request.assert_called_once()
    mocked_request_args = mocked_request.call_args.args

    payload = json.loads(mocked_request_args[3])
    assert payload["channel"] == "CEFJ9TJNL"
    assert "No challenge found" in payload["attachments"][0]["text"]

    async with client.app["pg"].acquire() as conn:
        await conn.execute(pg_insert(models.codewars).values(id="foo"))

    client.app["slack_client"]._request.reset_mock()
    await tasks.post_slack_codewars_challenge(client.app["slack_client"], client.app["pg"])

    mocked_request = client.app["slack_client"]._request
    mocked_request.assert_called_once()
    mocked_request_args = mocked_request.call_args.args

    payload = json.loads(mocked_request_args[3])
    assert payload["channel"] == "CEFJ9TJNL"
    assert payload["attachments"][0]["title_link"] == "https://www.codewars.com/kata/foo"


@mock.patch("time.time", mock.MagicMock(return_value=1534688291))
async def test_slack_admin_command(client):
    headers = {
        "X-Slack-Request-Timestamp": "1534688291",
        "X-Slack-Signature": "v0=b70aa6ce92e50274939779ffab81925a36cf53cd55cbcdb40db95710964f2826",
    }
    payload = {
        "command": "/admin",
        "trigger_id": "TEST-TRIGGER-ID",
        "channel_id": "TEST-CHANNEL-ID",
        "text": "TEST-TEXT",
    }
    r = await client.post("/bot/slack/commands", data=payload, headers=headers)
    assert r.status == 200
    assert client.app["slack_client"]._request.call_count == 1
    assert methods.DIALOG_OPEN.value[0] in client.app["slack_client"]._request.call_args.args

    data = json.loads(client.app["slack_client"]._request.call_args.args[3])
    assert data["trigger_id"] == "TEST-TRIGGER-ID"
    assert data["dialog"]["callback_id"] == "admin"


@mock.patch("time.time", mock.MagicMock(return_value=1534688291))
async def test_slack_snippet_command(client):
    headers = {
        "X-Slack-Request-Timestamp": "1534688291",
        "X-Slack-Signature": "v0=a598c6e4d907de0e312fa5bebbbcca4260724bcfb65176b6b26b0a35d33d1c2c",
    }
    payload = {
        "command": "/snippet",
        "trigger_id": "TEST-TRIGGER-ID",
        "channel_id": "TEST-CHANNEL-ID",
        "text": "TEST-TEXT",
    }
    r = await client.post("/bot/slack/commands", data=payload, headers=headers)
    assert r.status == 200

    assert client.app["slack_client"]._request.call_count == 2

    for call in client.app["slack_client"]._request.call_args_list:
        assert methods.CHAT_POST_MESSAGE.value[0] in call.args
        data = json.loads(call.args[3])
        assert data["channel"] == "TEST-CHANNEL-ID"


@mock.patch("time.time", mock.MagicMock(return_value=1534688291))
async def test_slack_howtoask_command(client):
    headers = {
        "X-Slack-Request-Timestamp": "1534688291",
        "X-Slack-Signature": "v0=bc0d78cd8dca215e0f79385ec642c69c43be708ba9c5f2687eaa627ac5a44194",
    }
    payload = {
        "command": "/howtoask",
        "trigger_id": "TEST-TRIGGER-ID",
        "channel_id": "TEST-CHANNEL-ID",
        "text": "TEST-TEXT",
    }
    r = await client.post("/bot/slack/commands", data=payload, headers=headers)
    assert r.status == 200

    assert client.app["slack_client"]._request.call_count == 1
    data = json.loads(client.app["slack_client"]._request.call_args.args[3])
    assert data["channel"] == "TEST-CHANNEL-ID"


@mock.patch("time.time", mock.MagicMock(return_value=1534688291))
async def test_slack_justask_command(client):
    headers = {
        "X-Slack-Request-Timestamp": "1534688291",
        "X-Slack-Signature": "v0=e2c4d085fb7718aa754a24820937f008b96a40b3e5b09801791d799ea0cbbbb0",
    }
    payload = {
        "command": "/justask",
        "trigger_id": "TEST-TRIGGER-ID",
        "channel_id": "TEST-CHANNEL-ID",
        "text": "TEST-TEXT",
    }
    r = await client.post("/bot/slack/commands", data=payload, headers=headers)
    assert r.status == 200

    assert client.app["slack_client"]._request.call_count == 1
    data = json.loads(client.app["slack_client"]._request.call_args.args[3])
    assert data["channel"] == "TEST-CHANNEL-ID"


@mock.patch("time.time", mock.MagicMock(return_value=1534688291))
async def test_slack_sponsors_command(client):
    headers = {
        "X-Slack-Request-Timestamp": "1534688291",
        "X-Slack-Signature": "v0=027940652b0636f53feeb517c8bdc30ee872f645d7a2d59217303d0846a133fe",
    }
    payload = {
        "command": "/sponsors",
        "trigger_id": "TEST-TRIGGER-ID",
        "channel_id": "TEST-CHANNEL-ID",
        "text": "TEST-TEXT",
    }
    r = await client.post("/bot/slack/commands", data=payload, headers=headers)
    assert r.status == 200

    assert client.app["slack_client"]._request.call_count == 1
    data = json.loads(client.app["slack_client"]._request.call_args.args[3])
    assert data["channel"] == "TEST-CHANNEL-ID"
