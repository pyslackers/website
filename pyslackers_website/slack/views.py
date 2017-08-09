import logging

from django.contrib import messages
from django.core.cache import cache
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView


from .forms import SlackInviteForm
from .tasks import send_slack_invite

logger = logging.getLogger('pyslackers.slack.views')


class SlackInvite(FormView):
    """Invite a user to slack"""
    template_name = 'slack/index.html'
    form_class = SlackInviteForm
    success_url = reverse_lazy('slack:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            slack_member_count=cache.get('slack_member_count', 0),
        )
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            email = form.cleaned_data['email']
            send_slack_invite.delay(email)
            messages.success(request, 'Invite sent, see you in Slack!')
            return self.form_valid(form)
        return self.form_invalid(form)
