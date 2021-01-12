import logging

from aiohttp import web
from slack import methods
from slack import commands
from slack.events import Message

from pyslackersweb.util.log import ContextAwareLoggerAdapter

logger = ContextAwareLoggerAdapter(logging.getLogger(__name__))


async def admin(request: web.Request, command: commands.Command) -> None:
    data = {
        "trigger_id": command["trigger_id"],
        "dialog": {
            "callback_id": "admin",
            "title": "Message the admin team",
            "elements": [
                {
                    "label": "Message",
                    "name": "message",
                    "type": "textarea",
                    "value": command["text"],
                }
            ],
        },
    }
    await request.app["slack_client"].query(url=methods.DIALOG_OPEN, data=data)


async def snippet(request: web.Request, command: commands.Command) -> None:
    """Post a message to the current channel about using snippets and backticks to visually
    format code."""
    response = Message()
    response["channel"] = command["channel_id"]
    response["unfurl_links"] = False

    response["text"] = (
        "Please use the snippet feature, or backticks, when sharing code. \n"
        "To include a snippet, click the :paperclip: on the left and hover over "
        "`Create new...` then select `Code or text snippet`.\n"
        "By wrapping the text/code with backticks (`) you get:\n"
        "`text formatted like this`\n"
        "By wrapping a multiple line block with three backticks (```) you can get:\n"
    )

    await request.app["slack_client"].query(url=methods.CHAT_POST_MESSAGE, data=response)

    response["text"] = (
        "```\n"
        "A multiline codeblock\nwhich is great for short snippets!\n"
        "```\n"
        "For more information on snippets, click "
        "<https://get.slack.help/hc/en-us/articles/204145658-Create-a-snippet|here>.\n"
        "For more information on inline code formatting with backticks click "
        "<https://get.slack.help/hc/en-us/articles/202288908-Format-your-messages#inline-code|here>."
    )

    await request.app["slack_client"].query(url=methods.CHAT_POST_MESSAGE, data=response)


async def ask_question(request: web.Request, command: commands.Command) -> None:
    response = Message()
    response["channel"] = command["channel_id"]
    response["unfurl_links"] = False

    response["text"] = (
        "If you have a question, please just ask it. Please do not ask for topic experts;  "
        "do not DM or ping random users. We cannot begin to answer a question until we actually get a question. \n\n"
        "<http://sol.gfxile.net/dontask.html|*Asking Questions*>"
    )

    await request.app["slack_client"].query(url=methods.CHAT_POST_MESSAGE, data=response)


async def howto_ask(request: web.Request, command: commands.Command) -> None:
    response = Message()
    response["channel"] = command["channel_id"]
    response["unfurl_links"] = True

    response["text"] = (
        "Knowing how to ask a good question is a highly invaluable skill that "
        "will benefit you greatly in any career. Two good resources for "
        "suggestions and strategies to help you structure and phrase your "
        "question to make it easier for those here to understand your problem "
        "and help you work to a solution are:\n\n"
        "• <https://www.mikeash.com/getting_answers.html>\n"
        "• <https://stackoverflow.com/help/how-to-ask>\n"
    )

    await request.app["slack_client"].query(url=methods.CHAT_POST_MESSAGE, data=response)


async def sponsors(request: web.Request, command: commands.Command) -> None:
    response = Message()
    response["channel"] = command["channel_id"]
    response["unfurl_links"] = False

    response["text"] = (
        "Thanks to our sponsors, <https://platform.sh|Platform.sh> and "
        "<https://sentry.io|Sentry> for providing hosting & services helping us "
        "host our <https://www.pyslackers.com|website> and Sir Bot-a-lot.\n"
        "If you are planning on using <https://sentry.io|Sentry> please use our <https://sentry.io/?utm_source=referral&utm_content=pyslackers&utm_campaign=community|"
        "referral code>."
    )

    await request.app["slack_client"].query(url=methods.CHAT_POST_MESSAGE, data=response)
