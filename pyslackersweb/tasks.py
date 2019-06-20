import dataclasses
import logging
from collections import Counter
from typing import List

from aiohttp import web

from .util.log import ContextAwareLoggerAdapter


logger = ContextAwareLoggerAdapter(logging.getLogger(__name__))


@dataclasses.dataclass(frozen=True)  # pylint: disable=too-few-public-methods
class Repository:
    name: str
    description: str
    href: str
    stars: int
    topics: List[str]


def sync_github_repositories(app: web.Application):
    session = app["client_session"]

    async def _sync_github() -> None:
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

            app["github_repositories"] = repositories[:6]
        except Exception:
            logger.exception("Error refreshing GitHub cache")
            raise

    return _sync_github


def sync_slack_timezones(app: web.Application):
    session = app["client_session"]

    async def _sync_slack():
        logger.debug("Refreshing slack user cache.")
        oauth_token = app["slack_token"]

        if oauth_token is None:
            logger.error("No slack oauth token set, unable to sync slack timezones.")
            return

        try:
            counter = Counter()
            while True:
                params = {}
                async with session.get(
                    "https://slack.com/api/users.list",
                    headers={"Authorization": f"Bearer {oauth_token}"},
                    params=params,
                ) as r:
                    result = await r.json()

                for user in result["members"]:
                    if user["deleted"] or user["is_bot"] or not user["tz"]:
                        continue

                    counter[user["tz"]] += 1

                # next_cursor can be an empty string. We need to check if the value is truthy
                if result.get("response_metadata", {}).get("next_cursor"):
                    params["cursor"] = result["response_metadata"]["next_cursor"]
                else:
                    break

            logger.debug(
                "Found %s users across %s timezones",
                sum(counter.values()),
                len(list(counter.keys())),
            )

            app.update(
                slack_timezones=dict(counter.most_common(100)),
                slack_user_count=sum(counter.values()),
            )
        except Exception:
            logger.exception("Error refreshing slack user cache")
            raise

    return _sync_slack
