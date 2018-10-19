from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from app.blog import models


class BlogSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return models.Post.objects.filter(published_at__isnull=False)

    def lastmod(self, obj: models.Post):
        return obj.updated_at

    def location(self, obj: models.Post):
        return reverse('blog:detail', kwargs={'slug': obj.slug})


class BlogStaticSitemap(Sitemap):
    def items(self):
        return 'blog:feed', 'blog:index'

    def location(self, obj):
        return reverse(obj)
