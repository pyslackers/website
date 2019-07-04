import random
from contextlib import asynccontextmanager
import pytest
import asyncpg

import pyslackersweb
import pyslackersweb.website.tasks

pytest_plugins = ("slack.tests.plugin",)


@pytest.fixture
async def client(aiohttp_client, slack_client):

    application = await pyslackersweb.app_factory()

    app_client = await aiohttp_client(application)
    app_client.app["scheduler"].shutdown()
    app_client.app["website_app"]["slack_client"] = slack_client

    return app_client


@pytest.fixture
async def cli_app(loop):  # pylint: disable=unused-argument
    app = await pyslackersweb.app_factory()
    async with pyslackersweb.cli.start_app(app):
        yield app


@pytest.fixture
async def database(loop):  # pylint: disable=unused-argument
    async with _database() as db:
        yield db


@asynccontextmanager
async def _database():
    id_ = random.randint(1, 100)
    dsn = pyslackersweb.settings.POSTGRESQL_DSN

    connection = await asyncpg.connect(dsn=dsn)
    await connection.execute(f"CREATE DATABASE test_{id_}")

    dsn_part = dsn.split("/")[:-1]
    dsn_part.append(f"test_{id_}")
    test_dsn = "/".join(dsn_part)

    async with asyncpg.create_pool(dsn=test_dsn) as pool:
        yield pool

    await connection.execute(f"DROP DATABASE test_{id_}")
    await connection.close()
