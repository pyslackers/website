import logging

from django.db import models

logger = logging.getLogger('pyslackers.marketing.models')


class BurnerDomain(models.Model):
    domain = models.TextField(unique=True)

    @classmethod
    def is_burner(cls, email: str):
        domain = email.split('@')[-1]
        try:
            logger.debug('Testing if domain %s is a suspected burner', domain)
            cls.objects.get(domain__iexact=domain)
            logger.debug('Domain %s is a suspected burner', domain)
            return True
        except cls.DoesNotExist:
            logger.debug('Domain %s not found in burner list', domain)
            return False
