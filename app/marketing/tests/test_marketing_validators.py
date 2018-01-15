import pytest
from django.forms import ValidationError

from app.marketing.models import BurnerDomain
from app.marketing.validators import validate_not_burner_domain


@pytest.mark.django_db
class TestValidateNotBurnerDomain:
    @pytest.mark.parametrize('email', [
        'foo@IAMATROLL.com',
        'foobar@iamAtRoLl.cOm',
        'foobarbaz@iamatroll.com',
    ])
    def test_catches_burners(self, email):
        BurnerDomain.objects.create(domain='iamatroll.com')
        with pytest.raises(ValidationError) as exc:
            validate_not_burner_domain(email)
        assert 'is a suspected throw' in str(exc)

    @pytest.mark.parametrize('email', [
        'foo@gmail.com',
        'foobar@gMAIL.cOm',
        'foobarbaz@gMaIl.cOm',
    ])
    def test_allows_ok_domain(self, email):
        assert validate_not_burner_domain(email) is None
