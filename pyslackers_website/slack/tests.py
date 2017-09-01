from django.core.cache import cache

from ..marketing.models import BurnerDomain
from .forms import SlackInviteForm
from .views import SlackInvite


class TestSlackInviteForm:
    """Tests to validate that the slack invite form runs
    the appropriate validations"""

    def test_blank_data(self):
        form = SlackInviteForm({})
        assert not form.is_valid()
        assert set(form.errors.keys()) == {'email', 'accept_tos'}

    def test_allows_non_burner_domain(self, monkeypatch):
        monkeypatch.setattr(BurnerDomain, 'is_burner', lambda x: False)

        form = SlackInviteForm({
            'email': 'foo@bar.com',
            'accept_tos': True,
        })
        assert form.is_valid()

    def test_invalidates_burner_domain(self, monkeypatch):
        monkeypatch.setattr(BurnerDomain, 'is_burner', lambda x: True)

        form = SlackInviteForm({
            'email': 'foo@bar.com',
            'accept_tos': True,
        })
        assert not form.is_valid()
        assert form.errors == {
            'email': ['Email is from a suspected burner domain'],
        }


class TestSlackInviteView:
    """Test case for Slack invite and map page"""

    def test_no_user_count(self, rf):
        """Assert slack member data is properly set without celery
        invocation"""
        request = rf.get('/slack/')
        response = SlackInvite.as_view()(request)
        assert response.status_code == 200
        assert response.context_data['slack_member_count'] == 0
        assert response.context_data['slack_member_tz_count'] == []

    def test_user_count_and_tz_count_from_cache(self, rf):
        """Assert slack member data is properly being pulled from cache"""
        slack_member_tz_count = (('TestArea', 5), ('TestArea2', 2))
        cache.set('slack_member_count', 7)
        cache.set('slack_member_tz_count', slack_member_tz_count)

        request = rf.get('/slack/')
        response = SlackInvite.as_view()(request)
        assert response.status_code == 200
        assert response.context_data['slack_member_count'] == 7
        assert response.context_data['slack_member_tz_count'] == slack_member_tz_count
