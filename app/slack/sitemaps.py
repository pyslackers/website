from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class SlackSitemap(Sitemap):
    priority = 1
    changefreq = 'weekly'

    def items(self):
        return 'slack:index',

    def location(self, obj):
        return reverse(obj)
