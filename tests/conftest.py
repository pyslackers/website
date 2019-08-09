import pytest

import pyslackersweb
import pyslackersweb.website.tasks

pytest_plugins = ("slack.tests.plugin",)


@pytest.fixture
async def client(aiohttp_client, slack_client):

    application = await pyslackersweb.app_factory()

    app_client = await aiohttp_client(application)
    app_client.app["scheduler"].shutdown()
    app_client.app["website_app"]["slack_client"] = slack_client
    app_client.app["website_app"]["slack_client_legacy"] = slack_client

    return app_client
