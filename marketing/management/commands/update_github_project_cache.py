from django.core.management.base import BaseCommand

from marketing.tasks import update_github_project_cache


class Command(BaseCommand):
    help = 'Force an update of the github repository cache'

    def handle(self, *args, **options):
        update_github_project_cache('pyslackers')
