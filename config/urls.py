from django.conf import settings
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('', include('pyslackers_website.marketing.urls')),
    path('blog/', include('pyslackers_website.blog.urls')),
    path('accounts/', include('allauth.urls')),
    path('slack/', include('pyslackers_website.slack.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
