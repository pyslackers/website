import logging
from collections import defaultdict
from typing import List, Optional

import requests
from django.conf import settings
from django.core.cache import cache
from celery import shared_task

from .util import SlackClient

logger = logging.getLogger('pyslackers.website.tasks')


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
    logger.debug('Sending a slack invite to %s', email)
    if channels is None:
        channels = settings.SLACK_JOIN_CHANNELS
    slack = SlackClient(settings.SLACK_OAUTH_TOKEN)
    slack.invite(email, channels, resend=resend)


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
def get_github_repos(org: str) -> None:
    """
    Retrieve the github repos for the org.
    :param org: Organization to get repos for
    """
    r = requests.get(f'https://api.github.com/orgs/{org}/repos',
                     headers={
                         # Include the "topics" :)
                         'Accept': 'application/vnd.github.mercy-preview+json'
                     },
                     params={
                         'type': 'public'
                     })
    r.raise_for_status()

    repos = []
    for repo in r.json():
        repos.append({
            'name': repo['name'],
            'description': repo['description'],
            'url': repo['html_url'],
            'updated_at': repo['updated_at'],
            'topics': repo.get('topics', []),
            'stargazers_count': repo.get('stargazers_count', 0),
        })
    repos.sort(key=lambda x: x['stargazers_count'], reverse=True)
    cache.set('github_projects', repos, None)
