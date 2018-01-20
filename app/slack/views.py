import logging
from collections import Counter

from django.http.response import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import FormView
from ratelimit.decorators import ratelimit

from .forms import SlackInviteForm
from .models import Membership
from .tasks import send_slack_invite

logger = logging.getLogger('pyslackersweb.slack')


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

    @ratelimit(key='ip', rate='5/h', method='POST')
    def post(self, request, *args, **kwargs):
        if request.limited:
            logger.warning('A slack invite request was rate limited',
                           extra={'request': request})
            return JsonResponse({'Rate Limited': [
                {'message': 'limit exceeded'}
            ]}, status=429)

        form = self.get_form()
        if form.is_valid():
            email = form.cleaned_data['email']
            return JsonResponse({
                'task_id': send_slack_invite.delay(email).id
            })

        return JsonResponse(form.errors.get_json_data(), status=400)


def timezone_json_view(request):
    """View to get the user timezones"""
    try:
        tzs = Membership.objects.latest().tz_count_json
    except Membership.DoesNotExist:
        tzs = {}
    return JsonResponse(dict(Counter(tzs).most_common(100)))
