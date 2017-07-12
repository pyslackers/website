from django.conf.urls import url

from .views import LatestPostFeed, PostDetail, PostIndex


urlpatterns = [
    url(r'^feed/$', LatestPostFeed()),
    url(r'^$', PostIndex.as_view(), name='index'),
    url(r'^(?P<slug>[\w-]+)/$', PostDetail.as_view(), name='detail'),
]
