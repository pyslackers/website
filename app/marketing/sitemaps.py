from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class MarketingSitemap(Sitemap):
    priority = 1
    changefreq = 'weekly'

    def items(self):
        return 'marketing:index', 'marketing:tos', 'marketing:version'

    def location(self, obj):
        return reverse(obj)
