import logging

import requests
from django.db import transaction
from django.core.cache import cache
from celery import shared_task

from .models import BurnerDomain
from .util import GithubClient

logger = logging.getLogger('pyslackers.website.tasks')


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
