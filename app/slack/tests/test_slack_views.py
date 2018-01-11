import json
import random

import pook
import pytest
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse

from app.slack.models import Membership
from app.slack.views import SlackInvite, timezone_json_view


@pytest.mark.django_db(transaction=True)
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

    def test_user_count_and_tz_count(self, rf):
        """Assert slack member data is properly being pulled"""
        slack_member_tz_count = {'TestArea': 5, 'TestArea2': 2}
        Membership.objects.create(bot_count=0, deleted_count=0, member_count=7,
                                  tz_count_json=slack_member_tz_count)

        request = rf.get(self.url)
        response = SlackInvite.as_view()(request)
        assert response.status_code == 200
        assert response.context_data['slack_member_count'] == 7

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

    def test_view_rate_limit(self, rf):
        try:
            remote_addr = '8.8.8.8'
            for i in range(3):
                request = rf.post(self.url, REMOTE_ADDR=remote_addr)
                SlackInvite.as_view()(request)

            request = rf.post(self.url, REMOTE_ADDR=remote_addr)
            response = SlackInvite.as_view()(request)
            assert response.status_code == 429
        finally:
            cache.delete_pattern(f'{settings.RATELIMIT_CACHE_PREFIX}*')

    @pook.post('https://slack.com/api/users.admin.invite', reply=200,
               content='urlencoded', response_json=dict(ok=True))
    def test_sends_slack_invite(self, rf, settings):
        settings.CELERY_ALWAYS_EAGER = True

        request = rf.post(self.url, data={
            'email': 'foo@gmail.com',
            'accept_tos': True,
        })
        response = SlackInvite.as_view()(request)
        assert response.status_code == 200
        assert 'task_id' in json.loads(response.content)
        assert pook.isdone()


@pytest.mark.django_db
class TestTimezoneJsonView:
    @property
    def url(self) -> str:
        return reverse('slack:timezones')

    def do_request(self, rf):
        response = timezone_json_view(rf.get(self.url))
        assert response.status_code == 200
        return json.loads(response.content)

    def test_empty_object_if_none(self, rf):
        body = self.do_request(rf)
        assert body == {}

    def test_json_format(self, rf):
        Membership.objects.create(bot_count=1, deleted_count=1, member_count=1,
                                  tz_count_json={
                                      'TestArea1': 10,
                                      'TestArea2': 5,
                                      'TestArea3': 100
                                  })
        body = self.do_request(rf)
        assert body == {
            'TestArea3': 100,
            'TestArea1': 10,
            'TestArea2': 5,
        }

    def test_only_gives_first_100(self, rf):
        areas = {f'TestArea{x}': random.choice(range(1, 50)) for x in range(105)}
        Membership.objects.create(bot_count=1, deleted_count=1, member_count=1,
                                  tz_count_json=areas)
        body = self.do_request(rf)
        assert len(body.keys()) == 100
