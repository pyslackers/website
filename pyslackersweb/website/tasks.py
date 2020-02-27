import asyncio
import dataclasses
import json
import logging
from collections import Counter
from typing import Any, Dict, List

import slack
from aiohttp import ClientSession
from aioredis.abc import AbcConnection as RedisConnection
from slack.io.abc import SlackAPI
from sqlalchemy.dialects.postgresql import insert as pg_insert

from pyslackersweb.models import domains, Source
from pyslackersweb.util.log import ContextAwareLoggerAdapter


logger = ContextAwareLoggerAdapter(logging.getLogger(__name__))

GITHUB_REPO_CACHE_KEY = "github:repos"

SLACK_CHANNEL_CACHE_KEY = "slack:channels"

SLACK_COUNT_CACHE_KEY = "slack:users:count"

SLACK_TZ_CACHE_KEY = "slack:users:timezones"


@dataclasses.dataclass(frozen=True)  # pylint: disable=too-few-public-methods
class Repository:
    name: str
    description: str
    href: str
    stars: int
    topics: List[str]


async def sync_github_repositories(
    session: ClientSession, redis: RedisConnection, *, cache_key: str = GITHUB_REPO_CACHE_KEY
) -> List[Repository]:
    logger.debug("Refreshing GitHub cache")
    repositories = []
    try:
        async with session.get(
            "https://api.github.com/orgs/pyslackers/repos",
            headers={"Accept": "application/vnd.github.mercy-preview+json"},
        ) as r:
            repos = await r.json()

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

        await redis.set(
            cache_key, json.dumps([dataclasses.asdict(repo) for repo in repositories[:6]])
        )
    except asyncio.CancelledError:
        logger.debug("Github cache refresh canceled")
    except Exception:  # pylint: disable=broad-except
        logger.exception("Error refreshing GitHub cache")

    return repositories


async def sync_slack_users(
    slack_client: SlackAPI,
    redis: RedisConnection,
    *,
    cache_key_tz: str = SLACK_TZ_CACHE_KEY,
    cache_key_count: str = SLACK_COUNT_CACHE_KEY,
) -> Counter:
    logger.debug("Refreshing slack users cache.")

    counter: Counter = Counter()
    try:
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

    except asyncio.CancelledError:
        logger.debug("Slack users cache refresh canceled")
    except Exception:  # pylint: disable=broad-except
        logger.exception("Error refreshing slack users cache")

    return counter


@dataclasses.dataclass(frozen=True)  # pylint: disable=too-few-public-methods
class Channel:
    id: str
    name: str
    topic: str
    purpose: str
    members: int


async def sync_slack_channels(
    slack_client: SlackAPI, redis: RedisConnection, *, cache_key: str = SLACK_CHANNEL_CACHE_KEY
) -> List[Channel]:
    logger.debug("Refreshing slack channels cache.")

    channels = []
    try:
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

        await redis.set(
            cache_key, json.dumps([dataclasses.asdict(channel) for channel in channels])
        )

    except asyncio.CancelledError:
        logger.debug("Slack channels cache refresh canceled")
    except Exception:  # pylint: disable=broad-except
        logger.exception("Error refreshing slack channels cache")

    return channels


async def sync_burner_domains(session: ClientSession, pg) -> List[Dict[str, Any]]:
    logger.debug("Refreshing burner domain list")

    try:
        async with session.get(
            "https://raw.githubusercontent.com/wesbos/burner-email-providers/master/emails.txt"
        ) as r:
            burners = [
                {"domain": x.lower(), "blocked": True, "source": Source.WESBOS}
                for x in (await r.text()).split("\n")
                if x
            ]

            async with pg.acquire() as conn:
                await conn.fetch(
                    pg_insert(domains)
                    .values(burners)
                    .on_conflict_do_nothing(index_elements=[domains.c.domain])
                )
            return burners
    except asyncio.CancelledError:
        pass
    return []
