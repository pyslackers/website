from typing import AsyncGenerator

from aiohttp import web


async def background_jobs(
    app: web.Application,  # pylint: disable=W0613
) -> AsyncGenerator[None, None]:
    # scheduler = app["scheduler"]
    # pg = app["pg"]
    # slack_client = app["slack_client"]

    # scheduler.add_job(
    #     tasks.post_slack_codewars_challenge,
    #     "interval",
    #     start_date=datetime.datetime(year=2021, month=1, day=7, hour=18, tzinfo=pytz.UTC),
    #     weeks=1,
    #     args=(slack_client, pg),
    # )

    yield
