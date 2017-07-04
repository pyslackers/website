from django.conf import settings
from django.core.cache import cache
from django.views.generic import FormView

from .forms import SlackInviteForm
from .tasks import send_slack_invite


class Index(FormView):
    template_name = 'marketing/index.html'
    form_class = SlackInviteForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            slack_member_count=cache.get('slack_member_count', None),
            github_repos=cache.get('github_projects', None),
        )
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            send_slack_invite.delay(settings.SLACK_OAUTH_TOKEN,
                                    form.data['email'],
                                    settings.SLACK_JOIN_CHANNELS)
            return self.form_valid(form)
        return self.form_invalid(form)
