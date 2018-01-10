import logging
from collections import Counter

from django.contrib import messages
from django.http.response import JsonResponse
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
            member_count = Membership.objects.latest().member_count
        except Membership.DoesNotExist:
            member_count = 0

        context.update(
            slack_member_count=member_count,
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


def timezone_json_view(request):
    """View to get the user timezones """
    try:
        tzs = Membership.objects.latest().tz_count_json
    except Membership.DoesNotExist:
        tzs = {}
    return JsonResponse(dict(Counter(tzs).most_common(100)))


def monthlymemberships_json_view(request):
    """View to get historical monthly membership data"""
    try:
        membership_history = Membership.objects.values_list('member_count', 'timestamp')
        membership_history_dict = build_membership_history_dict(membership_history)
    except Membership.DoesNotExist:
        membership_history_dict = {}
    return JsonResponse(membership_history_dict)


def build_membership_history_dict(membership_history):
    """Construct membership history dict"""
    counts = []
    xlabels = []
    is_first_record = True
    for member_count, timestamp in membership_history:
        counts.append(member_count)
        # force year to appear on first xaxis label (ie: Mar 17)
        if is_first_record:
            xlabel = timestamp.strftime('%b %y')
            is_first_record = False
        elif timestamp.strftime('%b%d') == 'Jan01':
            # new year detected, add MMM and YY to xlabels
            xlabel = timestamp.strftime('%b %y')
        elif timestamp.strftime('%d') == '01':
            # new month detected, add MMM to xlabels
            xlabel = timestamp.strftime('%b')
        else:
            xlabel = ""
        xlabels.append(xlabel)
    if len(xlabels) > 0 and not xlabels[-1]:
        xlabels[-1] = "Today"
    if not counts and not xlabels:
        membership_history_dict = {}
    else:
        membership_history_dict = {
            'counts': counts,
            'xlabels': xlabels,
        }
    return membership_history_dict
