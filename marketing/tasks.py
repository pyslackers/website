import logging
from typing import List, Optional

import requests
from django.db import transaction
from django.conf import settings
from django.core.cache import cache
from celery import shared_task

from .models import BurnerDomain, Membership
from .util import GithubClient, SlackClient

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
    logger.info('Sending a slack invite to %s', email)

    try:
        domain = email.split('@')[-1]
        BurnerDomain.objects.get(domain__iexact=domain)
        logger.info('Burner domain %s detected, bailing on invite request.',
                    domain)
        return
    except BurnerDomain.DoesNotExist:
        pass  # good news!

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


@shared_task
def update_github_project_cache(org: str) -> None:
    """
    Retrieve the github repos for the org.
    :param org: Organization to get repos for
    """
    logger.info('Retrieving github repos for org %s', org)
    gh = GithubClient()

    repos = []
    for repo in gh.get_org_repos(org):
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


@shared_task
def refresh_burner_domain_cache():
    """Refreshes our cache of known burner domains. Unfortunately
    we have had recent issues with burners and troll users and
    have decided to disallow invites to burners.

    This uses a list that Wes Bos has helped aggregate on
    GitHub."""
    logger.info('Refreshing burner domain cache')

    r = requests.get('https://raw.githubusercontent.com/wesbos/burner-email'
                     '-providers/master/emails.txt')
    r.raise_for_status()

    domains = set(r.iter_lines(decode_unicode=True))
    logger.info('Found %d domains', len(domains))
    with transaction.atomic():
        logger.info('Deleting out removed domains')
        count, _ = BurnerDomain.objects.exclude(domain__in=domains).delete()
        logger.info('Deleted %d domains', count)

        for domain in domains:
            _, is_new = BurnerDomain.objects.get_or_create(domain=domain)
            if is_new:
                logger.info('Added new domain %s', domain)
