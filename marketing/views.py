from django.conf import settings
from django.core.cache import cache
from django.views.generic import FormView, TemplateView
from django.utils import dateparse

from .forms import SlackInviteForm
from .tasks import send_slack_invite


class Index(FormView):
    template_name = 'marketing/index.html'
    form_class = SlackInviteForm
    success_url = '/'

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

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            send_slack_invite.delay(form.data['email'],
                                    channels=settings.SLACK_JOIN_CHANNELS)
            return self.form_valid(form)
        return self.form_invalid(form)


class TermsOfService(TemplateView):
    template_name = 'marketing/terms_of_service.html'
