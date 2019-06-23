import dataclasses
import json
import logging
from collections import Counter
from typing import List

import slack
from aiohttp import ClientSession
from aioredis.abc import AbcConnection
from slack.io.abc import SlackAPI

from pyslackersweb.util.log import ContextAwareLoggerAdapter


logger = ContextAwareLoggerAdapter(logging.getLogger(__name__))

GITHUB_REPO_CACHE_KEY = "github:repos"

SLACK_CHANNEL_CACHE_KEY = "slack:channels"

SLACK_COUNT_CACHE_KEY = "slack:user:count"

SLACK_TZ_CACHE_KEY = "slack:user:timezones"


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
    session: ClientSession, redis: AbcConnection, *, cache_key: str = GITHUB_REPO_CACHE_KEY
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


async def sync_slack_users(
    slack_client: SlackAPI,
    redis: AbcConnection,
    *,
    cache_key_tz: str = SLACK_TZ_CACHE_KEY,
    cache_key_count: str = SLACK_COUNT_CACHE_KEY,
):
    logger.debug("Refreshing slack users cache.")

    try:
        counter: Counter = Counter()
        async for user in slack_client.iter(slack.methods.USERS_LIST, minimum_time=3):
            if user["deleted"] or user["is_bot"] or not user["tz"]:
                continue

            counter[user["tz"]] += 1

        logger.debug(
            "Found %s users across %s timezones", sum(counter.values()), len(list(counter.keys()))
        )

        tx = redis.multi_exec()
        tx.delete(cache_key_tz)
        tx.hmset_dict(cache_key_tz, dict(counter.most_common(100)))
        tx.set(cache_key_count, str(sum(counter.values())))
        await tx.execute()
    except Exception:  # pylint: disable=broad-except
        logger.exception("Error refreshing slack user cache")
        return


async def sync_slack_channels(
    slack_client: SlackAPI, redis: AbcConnection, *, cache_key: str = SLACK_CHANNEL_CACHE_KEY
) -> None:
    logger.debug("Refreshing slack channels cache.")

    try:
        channels = []
        async for channel in slack_client.iter(slack.methods.CHANNELS_LIST):
            channels.append(
                Channel(
                    id=channel["id"],
                    name=channel["name"],
                    topic=channel["topic"]["value"],
                    purpose=channel["purpose"]["value"],
                    members=channel["num_members"],
                )
            )

        channels.sort(key=lambda c: c.name)

        logger.debug("Found %s slack channels", len(channels))

        await redis.set(cache_key, json.dumps([x.__dict__ for x in channels]))

    except Exception:  # pylint: disable=broad-except
        logger.exception("Error refreshing slack channels cache")
        return
