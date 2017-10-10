from django.core.cache import cache
from django.utils import dateparse
from django.views.generic import TemplateView
from django.http import JsonResponse

from pyslackers_website.slack.models import Membership
import os


class Index(TemplateView):
    template_name = 'marketing/index.html'

    def _github_repos(self):
        repos = cache.get('github_projects', [])[:6]
        for repo in repos:
            repo['updated_at'] = dateparse.parse_datetime(repo['updated_at'])
        return repos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_membership = Membership.latest()
        member_count = 0 if latest_membership is None else latest_membership.member_count
        context.update(
            slack_member_count=member_count,
            github_repos=self._github_repos(),
        )
        return context


class TermsOfService(TemplateView):
    template_name = 'marketing/terms_of_service.html'


def version(request):
    git_revision = os.getenv('APP_GIT_REVISION', '')
    return JsonResponse({'revision': git_revision})
