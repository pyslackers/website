from django.conf import settings
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('', include('app.marketing.urls')),
    path('blog/', include('app.blog.urls')),
    path('core/', include('app.core.urls')),
    path('slack/', include('app.slack.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
