from typing import AsyncGenerator

from aiohttp import ClientSession, web
from aioredis.abc import AbcConnection
from slack.io.aiohttp import SlackAPI

from . import tasks


async def background_jobs(app: web.Application) -> AsyncGenerator[None, None]:
    scheduler = app["scheduler"]
    client_session: ClientSession = app["client_session"]
    redis: AbcConnection = app["redis"]
    slack_client_: SlackAPI = app["slack_client"]
    pg = app["pg"]

    scheduler.add_job(
        tasks.sync_github_repositories, "cron", minute=30, args=(client_session, redis)
    )

    scheduler.add_job(tasks.sync_slack_users, "cron", minute=0, args=(slack_client_, redis))

    scheduler.add_job(tasks.sync_slack_channels, "cron", minute=15, args=(slack_client_, redis))

    scheduler.add_job(tasks.sync_burner_domains, "cron", hour=0, args=(client_session, pg))

    yield


async def slack_client(app: web.Application) -> AsyncGenerator[None, None]:
    app["slack_client"] = SlackAPI(token=app["slack_token"], session=app["client_session"])
    app["slack_client_legacy"] = SlackAPI(
        token=app["slack_invite_token"], session=app["client_session"]
    )
    yield
