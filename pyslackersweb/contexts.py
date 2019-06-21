import asyncio

from aiohttp import ClientSession, web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from slack.io.aiohttp import SlackAPI

from . import tasks


async def background_jobs(app: web.Application) -> None:
    app["scheduler"] = scheduler = AsyncIOScheduler()

    github_job = tasks.sync_github_repositories(app)
    scheduler.add_job(github_job, "interval", hours=6)

    slack_users_job = tasks.sync_slack_users(app)
    scheduler.add_job(slack_users_job, "interval", hours=6)

    slack_channels_job = tasks.sync_slack_channels(app)
    scheduler.add_job(slack_channels_job, "interval", hours=6)

    scheduler.start()

    loop = asyncio.get_running_loop()
    loop.create_task(github_job())
    loop.create_task(slack_users_job())
    loop.create_task(slack_channels_job())

    yield

    scheduler.shutdown()


async def client_session(app: web.Application) -> None:
    async with ClientSession(raise_for_status=True) as session:
        app["client_session"] = session
        yield


async def slack_client(app: web.Application) -> None:
    app["slack_client"] = SlackAPI(token=app["slack_token"], session=app["client_session"])
    yield
