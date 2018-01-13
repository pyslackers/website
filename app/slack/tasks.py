import logging
from collections import Counter
from typing import List, Optional

from celery import shared_task
from django.conf import settings

from .models import Invite, Membership
from .util import SlackException, SlackClient

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
    try:
        if slack.invite(email, channels, resend=resend):
            Invite.objects.get_or_create(email=email)
        logger.info('Successfully sent invite to %s', email)
    except SlackException as e:
        logger.error('Error sending invite to %s because %s', email, e)
        return {'error': str(e)}


@shared_task
def capture_snapshot_of_user_count() -> None:
    """Captures a snapshot of the user count in slack, this
    simply creates a record in the Membership table to track
    community growth over time."""
    slack = SlackClient(settings.SLACK_OAUTH_TOKEN)

    member_count = deleted_count = bot_count = 0
    time_zones = Counter()

    for member in slack.members():
        if member.get('is_bot'):
            bot_count += 1
        elif member.get('deleted'):
            deleted_count += 1
        else:
            member_count += 1
            tz = member.get('tz')
            if tz is not None:
                time_zones[tz] += 1

    Membership.objects.create(member_count=member_count,
                              deleted_count=deleted_count,
                              bot_count=bot_count,
                              tz_count_json=time_zones)
