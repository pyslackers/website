import pytest

import pyslackersweb
import pyslackersweb.website.tasks

from sqlalchemy import delete

pytest_plugins = ("slack.tests.plugin",)


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
        await conn.fetch(delete(pyslackersweb.sirbot.models.codewars))
