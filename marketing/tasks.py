import logging
from typing import Optional

import requests
from django.conf import settings
from django.core.cache import cache
from celery import shared_task

logger = logging.getLogger('pyslackers.website.tasks')


@shared_task
def send_slack_invite(token: str, email: str, channels: str, *,
                      resend: bool = True):
    """
    Send a slack invitation to the provided email
    :param token: Slack token to use, must be an admin user's token
    :param email: Email to send the invitation to
    :param channels: Channels for the user to join on invitation accept
    :param resend: If an invite has already been sent, send again.
    :return: None
    """
    logger.debug('Sending a slack invite to %s', email)
    r = requests.post('https://slack.com/api/users.admin.invite',
                      data={
                          'token': token,
                          'email': email,
                          'channels': channels,
                          'resend': resend,
                      })
    result = r.json()
    if result['ok']:
        logger.info('Slack invite sent successfully to %s', email)
    else:
        logger.error('Error sending invite: %s', result)


@shared_task
def get_slack_member_counts(token: Optional[str] = None):
    """
    Retrieve the number of members of the slack group that
    are active.
    :param token: Optional slack token to use, otherwise it
                  is retrieved from the settings.
    :return: None
    """
    if token is None:
        token = settings.SLACK_OAUTH_TOKEN

    logger.debug('Updating slack membership count.')
    r = requests.get('https://slack.com/api/users.list',
                     params=dict(token=token))
    r.raise_for_status()

    body = r.json()
    if body['ok']:
        member_count = sum(1 for x in body['members'] if not x['deleted'])
        cache.set('slack_member_count', member_count, None)
        logger.info('Updated slack member count, found %s active',
                    member_count)
    else:
        logger.error('Error refreshing slack member count: %s', body)


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
