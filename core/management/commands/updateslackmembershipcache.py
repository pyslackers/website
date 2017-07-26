from django.core.management.base import BaseCommand

from marketing.tasks import get_slack_member_counts


class Command(BaseCommand):
    help = 'Force an update of the slack membership counts'

    def handle(self, *args, **options):
        get_slack_member_counts()
