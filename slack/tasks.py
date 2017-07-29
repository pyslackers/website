import logging
from typing import List, Optional

from django.conf import settings
from django.core.cache import cache
from celery import shared_task

from .models import Membership
from .util import SlackClient

logger = logging.getLogger('pyslackers.slack.tasks')


@shared_task
def send_slack_invite(email: str, *, channels: Optional[List[str]] = None,
                      resend: bool = True):
    """
    Send a slack invitation to the provided email
    :param email: Email to send the invitation to
    :param channels: Channels for the user to join on invitation accept,
                     these must be channel IDs (not names)
    :param resend: If an invite has already been sent, send again.
    :return: None
    """
    logger.info('Sending a slack invite to %s', email)

    if channels is None:
        channels = settings.SLACK_JOIN_CHANNELS
    slack = SlackClient(settings.SLACK_OAUTH_TOKEN)
    if slack.invite(email, channels, resend=resend):
        logger.info('Successfully sent invite to %s', email)
    else:
        logger.error('Error sending invite to %s', email)


@shared_task
def update_slack_membership_cache() -> None:
    """Update the membership cache count."""
    slack = SlackClient(settings.SLACK_OAUTH_TOKEN)

    member_count = 0
    for member in slack.members():
        if member['deleted'] or member.get('is_bot'):
            continue
        member_count += 1

    cache.set('slack_member_count', member_count, None)


@shared_task
def capture_snapshot_of_user_count() -> None:
    """Captures a snapshot of the user count in slack, this
    simply creates a record in the Membership table to track
    community growth over time."""
    slack = SlackClient(settings.SLACK_OAUTH_TOKEN)

    member_count = deleted_count = bot_count = 0
    for member in slack.members():
        if member.get('is_bot'):
            bot_count += 1
        elif member.get('deleted'):
            deleted_count += 1
        else:
            member_count += 1

    Membership.objects.create(member_count=member_count,
                              deleted_count=deleted_count,
                              bot_count=bot_count)
