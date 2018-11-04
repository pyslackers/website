from django.contrib.postgres.fields import JSONField
from django.db import models


class Invite(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    blocked = models.BooleanField(default=False)

    class Meta:
        get_latest_by = 'created_at'


class Membership(models.Model):
    """This is intended as a snapshot of high level stats of the group."""
    member_count = models.IntegerField()
    deleted_count = models.IntegerField()
    bot_count = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    tz_count_json = JSONField(default=dict)

    class Meta:
        get_latest_by = 'timestamp'
