from django.db import models


class Membership(models.Model):
    member_count = models.IntegerField()
    deleted_count = models.IntegerField()
    bot_count = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
