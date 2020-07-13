import json
import logging

import slack.exceptions

from aiohttp import web
from aiohttp_jinja2 import template
from marshmallow.exceptions import ValidationError
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from pyslackersweb.util.log import ContextAwareLoggerAdapter
from pyslackersweb.models import domains, Source

from . import settings, database
from .models import InviteSchema
from .tasks import GITHUB_REPO_CACHE_KEY


logger = ContextAwareLoggerAdapter(logging.getLogger(__name__))

routes = web.RouteTableDef()


@routes.view("", name="index")
class Index(web.View):
    @template("index.html")
    async def get(self):
        redis = self.request.app["redis"]
        pg = self.request.app["pg"]

        async with pg.acquire() as conn:
            return {
                "member_count": await database.get_user_count(conn),
                "projects": json.loads(
                    await redis.get(GITHUB_REPO_CACHE_KEY, encoding="utf-8") or "{}"
                ),
                "sponsors": [
                    {
                        "image": self.request.app.router["static"].url_for(
                            filename="images/sponsor_platformsh.svg"
                        ),
                        "href": "https://platform.sh/?medium=referral&utm_campaign=sponsored_sites&utm_source=pyslackers",  # pylint: disable=line-too-long
                    },
                    {
                        "image": self.request.app.router["static"].url_for(
                            filename="images/sponsor_sentry.svg"
                        ),
                        "href": "https://sentry.io/?utm_source=referral&utm_content=pyslackers&utm_campaign=community",  # pylint: disable=line-too-long
                    },
                ],
            }


@routes.view("/slack", name="slack")
class SlackView(web.View):
    schema = InviteSchema()

    @property
    def pg(self):
        return self.request.app["pg"]

    async def shared_response(self):
        async with self.pg.acquire() as conn:
            return {
                "member_count": await database.get_user_count(conn),
                "member_timezones": await database.get_timezones(conn),
                "errors": {},
                "disable_invites": settings.DISABLE_INVITES,
            }

    async def allowed_email(self, email: str) -> bool:
        # this really should be in the schema validation, but it doesn't support async checks (yet).
        if "@" not in email:
            return False

        _, domain = email.lower().split("@")

        logger.info("Checking if domain %s should be allowed", domain)
        async with self.pg.acquire() as conn:
            row = await conn.fetchrow(
                select([domains.c.blocked, domains.c.domain]).where(domains.c.domain == domain)
            )
            if row is None:
                logger.info("Domain unknown, saving and allowing")
                await conn.fetchrow(
                    pg_insert(domains)
                    .values(domain=domain, blocked=False, source=Source.INVITE)
                    .on_conflict_do_nothing(index_elements=[domains.c.domain])
                )
                return True

        if row[domains.c.blocked.name]:
            logger.info("Domain '%s' on the blocklist, not allowing.", domain)
            return False
        return True

    @template("slack.html")
    async def get(self):
        return await self.shared_response()

    @template("slack.html")
    async def post(self):
        context = await self.shared_response()

        if settings.DISABLE_INVITES:
            return context

        try:
            invite = self.schema.load(await self.request.post())

            if await self.allowed_email(invite["email"]):
                await self.request.app["slack_client_legacy"].query(
                    url="users.admin.invite", data={"email": invite["email"], "resend": True}
                )
            context["success"] = True
        except ValidationError as e:
            context["errors"] = e.normalized_messages()
        except slack.exceptions.SlackAPIError as e:
            logger.warning("Error sending slack invite: %s", e.error, extra=e.data)
            context["errors"].update(non_field=[e.error])
        except slack.exceptions.HTTPException:
            logger.exception("Error contacting slack API")
            context["errors"].update(non_field=["Error contacting slack API"])

        return context
