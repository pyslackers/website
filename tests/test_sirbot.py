import pytest

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
async def test_readthedocs_notification(client, slack_mock, payload, expected):
    if expected:
        slack_mock.success({"ok": True, "build": payload["build"], "name": payload["name"]})
    else:
        slack_mock.success()

    r = await client.post("/bot/readthedocs", json=payload)
    assert r.status == 200

    # Assert we send a message to slack only when expected
    if expected:
        slack_mock.query.assert_called_once()
        mock_args = slack_mock.query.call_args.args
        mock_kwargs = slack_mock.query.call_args.kwargs

        assert mock_args[0] == methods.CHAT_POST_MESSAGE
        assert mock_kwargs["data"]["channel"] == settings.READTHEDOCS_NOTIFICATION_CHANNEL
        assert expected["project"] in mock_kwargs["data"]["text"]
        assert expected["status"] in mock_kwargs["data"]["text"]
    else:
        slack_mock.query.assert_not_called()


async def test_readthedocs_notification_missing_name(client, slack_mock):
    slack_mock.success()

    r = await client.post("/bot/readthedocs", json={})
    assert r.status == 400

    # Assert we did not send a message to slack
    slack_mock.query.assert_not_called()


async def test_task_codewars_challenge(client, slack_mock, caplog):
    await tasks.post_slack_codewars_challenge(client.app["slack_client"], client.app["pg"])

    slack_mock.query.assert_called_once()
    mocked_query_args = slack_mock.query.call_args.kwargs

    payload = mocked_query_args["data"]
    assert payload["channel"] == "CEFJ9TJNL"
    assert "No challenge found" in payload["attachments"][0]["text"]

    async with client.app["pg"].acquire() as conn:
        await conn.execute(pg_insert(models.codewars).values(id="foo"))

    slack_mock.query.reset_mock()
    await tasks.post_slack_codewars_challenge(client.app["slack_client"], client.app["pg"])

    slack_mock.query.assert_called_once()
    mocked_query_args = slack_mock.query.call_args.kwargs

    payload = mocked_query_args["data"]
    assert payload["channel"] == "CEFJ9TJNL"
    assert payload["attachments"][0]["title_link"] == "https://www.codewars.com/kata/foo"
