import pytest
from django.forms import ValidationError

from app.slack.validators import validate_not_duplicate_email
from app.slack.models import Invite


@pytest.mark.django_db
class TestValidateNotBannedEmail:
    def test_rejects_duplicate(self):
        Invite.objects.bulk_create([
            Invite(email='foo@bar.com', blocked=True),
            Invite(email='f.o.o@bar.com'),
        ])

        with pytest.raises(ValidationError) as exc:
            validate_not_duplicate_email('foo+bar@bar.com')
        assert 'Email appears to be a duplicate' in str(exc)

    def test_ignores_duplicate_if_not_blocked(self):
        Invite.objects.bulk_create([
            Invite(email='foo@bar.com', blocked=False),
            Invite(email='f.o.o@bar.com', blocked=False),
        ])

        validate_not_duplicate_email('foo+bar@bar.com')

    def test_does_not_incorrectly_flag_different_domain(self):
        Invite.objects.bulk_create([
            Invite(email='foo@bar.com', blocked=True),
            Invite(email='f.o.o@bar.com', blocked=True),
        ])
        validate_not_duplicate_email('foo+bar@baz.com')
