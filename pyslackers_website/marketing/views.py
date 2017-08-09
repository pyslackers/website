from django.core.cache import cache
from django.utils import dateparse
from django.views.generic import TemplateView


class Index(TemplateView):
    template_name = 'marketing/index.html'

    def _github_repos(self):
        repos = cache.get('github_projects', [])[:6]
        for repo in repos:
            repo['updated_at'] = dateparse.parse_datetime(repo['updated_at'])
        return repos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            slack_member_count=cache.get('slack_member_count', 0),
            github_repos=self._github_repos(),
        )
        return context


class TermsOfService(TemplateView):
    template_name = 'marketing/terms_of_service.html'
