import pook
import pytest
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse
from ratelimit.exceptions import Ratelimited

from pyslackers_website.slack.models import Membership
from pyslackers_website.slack.views import SlackInvite


@pytest.mark.django_db
class TestSlackInviteView:
    """Test case for Slack invite and map page"""
    @property
    def url(self) -> str:
        return reverse('slack:index')

    def test_no_user_count(self, rf):
        """Assert slack member data is properly set without celery
        invocation"""
        request = rf.get(self.url)
        response = SlackInvite.as_view()(request)
        assert response.status_code == 200
        assert response.context_data['slack_member_count'] == 0
        assert response.context_data['slack_member_tz_count'] == {}

    def test_user_count_and_tz_count(self, rf):
        """Assert slack member data is properly being pulled"""
        slack_member_tz_count = {'TestArea': 5, 'TestArea2': 2}
        Membership.objects.create(bot_count=0, deleted_count=0, member_count=7,
                                  tz_count_json=slack_member_tz_count)

        request = rf.get(self.url)
        response = SlackInvite.as_view()(request)
        assert response.status_code == 200
        assert response.context_data['slack_member_count'] == 7
        assert response.context_data['slack_member_tz_count'] == slack_member_tz_count

    def test_gets_latest_user_and_tz_count(self, rf):
        Membership.objects.create(bot_count=0, deleted_count=0, member_count=7,
                                  tz_count_json={
                                      'TestArea1': 2,
                                  })

        membership_growth = [
            dict(bot_count=1, deleted_count=1, member_count=1, tz_count_json={'TestArea1': 1}),
            dict(bot_count=1, deleted_count=1, member_count=5, tz_count_json={'TestArea1': 2, 'TestArea2': 4}),
            dict(bot_count=1, deleted_count=1, member_count=15,
                 tz_count_json={'TestArea1': 2, 'TestArea2': 4, 'TestArea3': 9}),
        ]

        view = SlackInvite.as_view()
        for new_latest_membership in membership_growth:
            new_membership = Membership.objects.create(**new_latest_membership)
            request = rf.get(self.url)
            response = view(request)

            assert response.status_code == 200
            assert response.context_data['slack_member_count'] == new_membership.member_count
            assert response.context_data['slack_member_tz_count'] == new_membership.tz_count_json

    def test_view_rate_limit(self, rf):
        """"""
        try:
            remote_addr = '8.8.8.8'
            for i in range(10):
                request = rf.post(self.url, REMOTE_ADDR=remote_addr)
                SlackInvite.as_view()(request)

            request = rf.post(self.url, REMOTE_ADDR=remote_addr)
            with pytest.raises(Ratelimited):
                SlackInvite.as_view()(request)
        finally:
            cache.delete_pattern(f'{settings.RATELIMIT_CACHE_PREFIX}*')

    @pook.post('https://slack.com/api/users.admin.invite', reply=200,
               content='urlencoded', response_json=dict(ok=True))
    def test_sends_slack_invite(self, rf):
        request = rf.post(self.url, data={
            'email': 'foo@gmail.com',
            'accept_tos': True,
        })
        SessionMiddleware().process_request(request)
        MessageMiddleware().process_request(request)

        response = SlackInvite.as_view()(request)
        assert response.status_code == 302
        assert pook.isdone()
        assert len(request._messages) == 1  # don't really care about the text
