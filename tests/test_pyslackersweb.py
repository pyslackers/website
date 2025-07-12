import logging

from pyslackersweb import tasks, contexts, models


async def test_task_sync_slack_users(client, caplog):
    assert await contexts._is_empty_table(client.app["pg"], models.SlackUsers.c.id)

    await tasks.sync_slack_users(client.app["slack_client"], client.app["pg"])

    assert not (await contexts._is_empty_table(client.app["pg"], models.SlackUsers.c.id))

    for record in caplog.records:
        assert record.levelno <= logging.INFO


async def test_task_sync_slack_channels(client, caplog):
    assert await contexts._is_empty_table(client.app["pg"], models.SlackChannels.c.id)

    await tasks.sync_slack_channels(client.app["slack_client"], client.app["pg"])

    assert not (await contexts._is_empty_table(client.app["pg"], models.SlackChannels.c.id))

    for record in caplog.records:
        assert record.levelno <= logging.INFO
