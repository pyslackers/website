from django.db import models
from django.contrib.postgres.fields import JSONField


class Membership(models.Model):
    """This is intended as a snapshot of high level stats of the group."""
    member_count = models.IntegerField()
    deleted_count = models.IntegerField()
    bot_count = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    tz_count_json = JSONField(default={})

    @classmethod
    def latest(cls):
        return cls.objects.order_by('-timestamp').last()
