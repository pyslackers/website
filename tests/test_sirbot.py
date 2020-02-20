from slack import methods

from pyslackersweb.sirbot import settings


async def test_readthedocs_notification(client):
    r = await client.post("/bot/readthedocs", json={"name": "pyslackers/website"})
    assert r.status == 200

    # Assert we send a message to slack
    client.app["slack_client"]._request.assert_called_once()
    assert methods.CHAT_POST_MESSAGE.value[0] in client.app["slack_client"]._request.call_args.args
    assert (
        settings.READTHEDOCS_NOTIFICATION_CHANNEL
        in client.app["slack_client"]._request.call_args.args[3]
    )


async def test_readthedocs_notification_missing_name(client):
    r = await client.post("/bot/readthedocs", json={})
    assert r.status == 400

    # Assert we did not send a message to slack
    assert not client.app["slack_client"]._request.called
