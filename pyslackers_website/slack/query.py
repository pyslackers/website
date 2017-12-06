from django.db import models


class MembershipQuerySet(models.QuerySet):
    """Custom queryset for memberships"""

    def most_recent(self):
        return self.order_by('-timestamp').first()
