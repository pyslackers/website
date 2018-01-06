import logging
from collections import Counter

import json

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
        try:
            latest_membership = Membership.objects.latest()
            member_count = latest_membership.member_count
            tz_count_json = latest_membership.tz_count_json
            membership_history_json = self.get_membership_history_json()
        except Membership.DoesNotExist:
            member_count = 0
            tz_count_json = {}
            membership_history_json = {}

        context.update(
            slack_member_count=member_count,
            slack_member_tz_count=Counter(tz_count_json).most_common(100),
            slack_membership_history_json=membership_history_json,
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

    def get_membership_history_json(self):
        """ Build membership history JSON """
        counts = []
        xlabels = []
        is_first_record = True

        membership_history = Membership.objects.values_list('member_count', 'timestamp')
        for member_count, timestamp in membership_history:
            counts.append(member_count)
            if is_first_record:
                # force year to appear on first xaxis label (ie: Mar 17)
                xlabel = timestamp.strftime('%b %y')
                is_first_record = False
            elif timestamp.strftime('%b%d') == 'Jan01':
                # new year detected, add MMM and YY to xlabels
                xlabel = timestamp.strftime('%b %y')
            elif timestamp.strftime('%d') == '01':
                # new month detected, add MMM to xlabels
                xlabel = timestamp.strftime('%b')
            else:
                continue

            xlabels.append(xlabel)
        membership_history_json = {
                                        'counts': counts,
                                        'xlabels': xlabels,
                                    }
        return json.dumps(membership_history_json)
