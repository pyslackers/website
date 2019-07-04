import json
import logging

from aiohttp import web
from aiohttp_jinja2 import template
from marshmallow.exceptions import ValidationError

from pyslackersweb.util.log import ContextAwareLoggerAdapter

from .models import InviteSchema
from .tasks import GITHUB_REPO_CACHE_KEY, SLACK_COUNT_CACHE_KEY, SLACK_TZ_CACHE_KEY


logger = ContextAwareLoggerAdapter(logging.getLogger(__name__))

routes = web.RouteTableDef()


@routes.view("", name="index")
class Index(web.View):
    @template("index.html")
    async def get(self):
        redis = self.request.app["redis"]

        return {
            "member_count": int((await redis.get(SLACK_COUNT_CACHE_KEY, encoding="utf-8")) or 0),
            "projects": json.loads(await redis.get(GITHUB_REPO_CACHE_KEY, encoding="utf-8")),
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

    async def shared_response(self):
        redis = self.request.app["redis"]

        return {
            "member_count": int((await redis.get(SLACK_COUNT_CACHE_KEY, encoding="utf-8")) or 0),
            "member_timezones": await redis.hgetall(SLACK_TZ_CACHE_KEY, encoding="utf-8"),
            "errors": {},
        }

    @template("slack.html")
    async def get(self):
        return await self.shared_response()

    @template("slack.html")
    async def post(self):
        context = await self.shared_response()

        try:
            invite = self.schema.load(await self.request.post())
            async with self.request.app["client_session"].post(
                "https://slack.com/api/users.admin.invite",
                headers={"Authorization": f"Bearer {self.request.app['slack_invite_token']}"},
                data={"email": invite["email"], "resend": True},
            ) as r:
                body = await r.json()

            if body["ok"]:
                context["success"] = True
            else:
                logger.warning("Error sending slack invite: %s", body["error"], extra=body)
                context["errors"].update(non_field=[body["error"]])
        except ValidationError as e:
            context["errors"] = e.normalized_messages()

        return context
