from django.core.management.base import BaseCommand

from pyslackers_website.marketing import refresh_burner_domain_cache


class Command(BaseCommand):
    help = 'Refresh the burner domain cache'

    def handle(self, *args, **options):
        refresh_burner_domain_cache()
