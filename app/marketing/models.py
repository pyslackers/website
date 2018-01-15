from django.db import models


class BurnerDomain(models.Model):
    domain = models.TextField(unique=True)
