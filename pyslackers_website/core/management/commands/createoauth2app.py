"""
This doesn't really belong here, but you can't create
commands at the main config package :(.
"""
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Add a new oauth2 application'

    def add_arguments(self, parser):
        parser.add_argument('--client-id', type=str, action='store',
                            required=True, dest='client_id')
        parser.add_argument('--client-secret', type=str, action='store',
                            required=True, dest='client_secret')
        parser.add_argument('--provider', type=str, action='store',
                            required=True, dest='provider',
                            choices=['twitter', 'google'])
        parser.add_argument('--name', type=str, action='store', default='',
                            dest='name')

    def handle(self, *args, **options):
        site = Site.objects.first()
        name = options['name']
        if not name:
            name = options['provider'] + '-local'
        site.socialapp_set.create(provider=options['provider'],
                                  name=name,
                                  client_id=options['client_id'],
                                  secret=options['client_secret'])
