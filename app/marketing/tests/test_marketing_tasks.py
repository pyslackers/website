import random
from datetime import datetime

import pook
from django.core.cache import cache

from app.marketing.tasks import (
    update_github_project_cache,
)


def generate_repo_dict(name):
    choices = [str(x) for x in range(10)]
    return {
        'name': name,
        'description': f'My {name} repo',
        'html_url': f'https://github.com/foobar/{name}/',
        'topics': random.choices(choices, k=random.choice(range(5))),
        'stargazers_count': random.choice(range(25)),  # high aspirations...
        'archived': random.choice([True, False]),
        'updated_at': datetime.now().isoformat()
    }


class TestUpdateGithubProjectCache:
    @pook.get('https://api.github.com/orgs/foobar/repos',
              # Note: this is a partial representation...
              reply_json=[generate_repo_dict(x) for x in [
                  'first', 'second', 'third', 'fourth', 'fizif!'
              ]])
    def test_excludes_archived_repos(self):
        update_github_project_cache('foobar')
        projects = cache.get('github_projects')
        assert not any(x.get('archived') is False for x in projects)

    @pook.get('https://api.github.com/orgs/foobar/repos',
              # Note: this is a partial representation...
              reply_json=[generate_repo_dict(x) for x in [
                  'first', 'second', 'third', 'fourth', 'fizif!'
              ]])
    def test_orders_by_stars(self):
        update_github_project_cache('foobar')
        projects = cache.get('github_projects')
        last_stars = 0
        for project in projects:
            assert last_stars <= project['stargazers_count']
