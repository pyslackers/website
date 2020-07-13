import asyncio
import dataclasses
import json
import logging
from typing import Any, Dict, List

from aiohttp import ClientSession
from aioredis.abc import AbcConnection as RedisConnection
from sqlalchemy.dialects.postgresql import insert as pg_insert

from pyslackersweb.models import domains, Source
from pyslackersweb.util.log import ContextAwareLoggerAdapter


logger = ContextAwareLoggerAdapter(logging.getLogger(__name__))

GITHUB_REPO_CACHE_KEY = "github:repos"


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
