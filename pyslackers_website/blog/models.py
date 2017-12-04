from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import slugify

from .query import PostQuerySet, TagQuerySet

User = get_user_model()


class Post(models.Model):
    """Post"""
    title = models.TextField(unique=True)
    slug = models.SlugField(editable=False, max_length=255)
    content = models.TextField()  # stored as markdown
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    published_at = models.DateTimeField(null=True, blank=True)
    tags = models.ManyToManyField('Tag', related_name='posts')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PostQuerySet.as_manager()

    def save(self, *args, **kwargs):
        """save"""
        if not self.id:
            # Only set the slug once to not break perma-links
            self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Tag"""
    name = models.CharField(max_length=25, unique=True, db_index=True)

    objects = TagQuerySet.as_manager()

    def save(self, *args, **kwargs):
        """save"""
        self.name = self.name.lower()
        super(Tag, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
