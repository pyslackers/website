import pytest

from slack import methods

from pyslackersweb.sirbot import settings


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
