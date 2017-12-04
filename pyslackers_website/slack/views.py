import logging
from collections import Counter

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView
from ratelimit.decorators import ratelimit

from .forms import SlackInviteForm
from .models import Membership
from .tasks import send_slack_invite

logger = logging.getLogger('pyslackers.slack.views')


class SlackInvite(FormView):
    """Invite a user to slack"""
    template_name = 'slack/index.html'
    form_class = SlackInviteForm
    success_url = reverse_lazy('slack:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_membership = Membership.latest()
        member_count = 0 if latest_membership is None else latest_membership.member_count
        tz_count_json = {} if latest_membership is None else latest_membership.tz_count_json

        context.update(
            slack_member_count=member_count,
            slack_member_tz_count=Counter(tz_count_json).most_common(100),
        )
        return context

    @ratelimit(key='ip', rate='10/h', method='POST', block=True)
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            email = form.cleaned_data['email']
            send_slack_invite.delay(email)
            messages.success(request, 'Invite sent, see you in Slack!')
            return self.form_valid(form)
        return self.form_invalid(form)
