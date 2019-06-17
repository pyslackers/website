from aiohttp import web
from aiohttp_jinja2 import template
from marshmallow.exceptions import ValidationError

from .models import InviteSchema

routes = web.RouteTableDef()


@routes.view("", name="index")
class Index(web.View):
    @template("index.html")
    async def get(self):
        return {
            "member_count": self.request.app["slack_user_count"],
            "projects": self.request.app["github_repositories"],
            "sponsors": [
                {
                    "image": "/static/images/sponsor_platformsh.svg",
                    "href": "https://platform.sh/?medium=referral&utm_campaign=sponsored_sites&utm_source=pyslackers",  # pylint: disable=line-too-long
                },
                {
                    "image": "/static/images/sponsor_sentry.svg",
                    "href": "https://sentry.io/?utm_source=referral&utm_content=pyslackers&utm_campaign=community",  # pylint: disable=line-too-long
                },
            ],
        }


@routes.view("/slack", name="slack")
class SlackView(web.View):
    schema = InviteSchema()

    async def shared_response(self):
        return {
            "member_count": self.request.app["slack_user_count"],
            "member_timezones": self.request.app["slack_timezones"],
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
                headers={"Authorization": f"Bearer {self.request.app['slack_oauth_token']}"},
                data={"email": invite["email"], "resend": True},
            ) as r:
                body = await r.json()

            if body["ok"]:
                context["success"] = True
            else:
                context["errors"].update(non_field=[body["error"]])
        except ValidationError as e:
            context["errors"] = e.normalized_messages()

        return context
