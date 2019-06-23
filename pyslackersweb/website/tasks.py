import dataclasses
import json
import logging
from collections import Counter
from typing import List, Awaitable, Callable

import slack
from aiohttp import ClientSession, web
from aioredis.abc import AbcConnection

from pyslackersweb.util.log import ContextAwareLoggerAdapter


logger = ContextAwareLoggerAdapter(logging.getLogger(__name__))


@dataclasses.dataclass(frozen=True)  # pylint: disable=too-few-public-methods
class Repository:
    name: str
    description: str
    href: str
    stars: int
    topics: List[str]


@dataclasses.dataclass(frozen=True)  # pylint: disable=too-few-public-methods
class Channel:
    id: str
    name: str
    topic: str
    purpose: str
    members: int


async def sync_github_repositories(
    session: ClientSession, redis: AbcConnection, *, cache_key: str = "github:repos"
) -> None:
    logger.debug("Refreshing GitHub cache")
    try:
        async with session.get(
            "https://api.github.com/orgs/pyslackers/repos",
            headers={"Accept": "application/vnd.github.mercy-preview+json"},
        ) as r:
            repos = await r.json()

        repositories = []
        for repo in repos:
            if repo["archived"]:
                continue

            repositories.append(
                Repository(
                    repo["name"],
                    repo["description"],
                    repo["html_url"],
                    repo["stargazers_count"],
                    repo["topics"],
                )
            )

        logger.debug("Found %s non-archived repositories", len(repositories))

        repositories.sort(key=lambda r: r.stars, reverse=True)

        await redis.set(cache_key, json.dumps([x.__dict__ for x in repositories[:6]]))

    except Exception:
        logger.exception("Error refreshing GitHub cache")
        raise


def sync_slack_users(app: web.Application) -> Callable[[], Awaitable[None]]:
    client = app["slack_client"]

    async def _sync_slack_users() -> None:
        logger.debug("Refreshing slack users cache.")
        oauth_token = app["slack_token"]

        if oauth_token is None:
            logger.error("No slack oauth token set, unable to sync slack users.")
            return

        try:
            counter: Counter = Counter()
            async for user in client.iter(slack.methods.USERS_LIST, minimum_time=3):
                if user["deleted"] or user["is_bot"] or not user["tz"]:
                    continue

                counter[user["tz"]] += 1

            logger.debug(
                "Found %s users across %s timezones",
                sum(counter.values()),
                len(list(counter.keys())),
            )

            app.update(
                slack_timezones=dict(counter.most_common(100)),
                slack_user_count=sum(counter.values()),
            )
        except Exception:  # pylint: disable=broad-except
            logger.exception("Error refreshing slack user cache")
            return

    return _sync_slack_users


def sync_slack_channels(app: web.Application) -> Callable[[], Awaitable[None]]:
    client = app["slack_client"]

    async def _sync_slack_channel() -> None:
        logger.debug("Refreshing slack channels cache.")
        oauth_token = app["slack_token"]

        if oauth_token is None:
            logger.error("No slack oauth token set, unable to sync slack channels.")
            return

        try:
            channels = []
            async for channel in client.iter(slack.methods.CHANNELS_LIST):
                channels.append(
                    Channel(
                        id=channel["id"],
                        name=channel["name"],
                        topic=channel["topic"]["value"],
                        purpose=channel["purpose"]["value"],
                        members=channel["num_members"],
                    )
                )

            logger.debug("Found %s slack channels", len(channels))

            app.update(slack_channels=sorted(channels, key=lambda c: c.name))

        except Exception:  # pylint: disable=broad-except
            logger.exception("Error refreshing slack channels cache")
            return

    return _sync_slack_channel
