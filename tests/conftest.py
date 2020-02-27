import pytest

import pyslackersweb
import pyslackersweb.website.tasks

from sqlalchemy import delete
from pyslackersweb.models import domains

pytest_plugins = ("slack.tests.plugin",)


@pytest.fixture
async def client(aiohttp_client, slack_client):

    application = await pyslackersweb.app_factory()

    app_client = await aiohttp_client(application)
    app_client.app["scheduler"].shutdown()

    pyslackersweb.contexts._register_in_app(app_client.app, "slack_client", slack_client)
    pyslackersweb.contexts._register_in_app(app_client.app, "slack_client_legacy", slack_client)

    yield app_client

    # cleanup database
    async with app_client.app["pg"].acquire() as conn:
        await conn.fetch(delete(domains))
