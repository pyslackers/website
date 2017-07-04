from django.conf.urls import url

from .views import PostDetail, PostIndex


urlpatterns = [
    url(r'^$', PostIndex.as_view(), name='index'),
    url(r'^(?P<slug>[\w-]+)/$', PostDetail.as_view(), name='detail'),
]
