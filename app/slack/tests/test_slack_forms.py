from app.marketing.models import BurnerDomain
from app.slack.forms import SlackInviteForm


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
            'email': ['Email is from a suspected throw away domain'],
        }
