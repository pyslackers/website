from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    url(r'^', include('pyslackers_website.marketing.urls', namespace='marketing')),
    url(r'^blog/', include('pyslackers_website.blog.urls', namespace='blog')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^slack/', include('pyslackers_website.slack.urls', namespace='slack')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
