from django.db import models


class PostQuerySet(models.QuerySet):
    """Custom queryset for blog posts."""

    def published(self):
        """Return only posts that are published."""
        return self.filter(published_at__isnull=False).order_by('-published_at')


class TagQuerySet(models.QuerySet):
    """Custom queryset for tags."""

    def names(self):
        """Return only tags that are actually attached to a published post.

        We want unique names here, ordered by name
        """
        return self.filter(posts__published_at__isnull=False) \
            .exclude(posts=None) \
            .order_by('name') \
            .distinct('name')
