from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include

from app.blog.sitemaps import BlogSitemap, BlogStaticSitemap
from app.marketing.sitemaps import MarketingSitemap
from app.slack.sitemaps import SlackSitemap


sitemaps = {
    'blog': BlogSitemap,
    'blog-static': BlogStaticSitemap,
    'marketing': MarketingSitemap,
    'slack': SlackSitemap
}

urlpatterns = [
    path('', include('app.marketing.urls')),
    path('blog/', include('app.blog.urls')),
    path('core/', include('app.core.urls')),
    path('slack/', include('app.slack.urls')),
    path('admin/', admin.site.urls),
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='sitemap'
    )
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
