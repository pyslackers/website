
from django.core.cache import cache
from django.utils import dateparse
from django.views.generic import TemplateView
from django.http import JsonResponse

from app.slack.models import Membership
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
        try:
            member_count = Membership.objects.latest().member_count
        except Membership.DoesNotExist:
            member_count = 0

        context.update(
            slack_member_count=member_count,
            github_repos=self._github_repos(),
        )
        return context


class TermsOfService(TemplateView):
    template_name = 'marketing/terms_of_service.html'


class GoogleSearchVerificationView(TemplateView):
    """
    View required for google domain ownership verification.
    """
    template_name = 'marketing/google5e9627529a176ba5.html'


def version(request):
    git_revision = os.getenv('APP_GIT_REVISION', '')
    return JsonResponse({'revision': git_revision})
