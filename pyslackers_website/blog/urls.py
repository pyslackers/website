from django.conf.urls import url

from .views import LatestPostFeed, PostDetailView, PostListView


urlpatterns = [
    url(r'^feed/$', LatestPostFeed()),
    url(r'^$', PostListView.as_view(), name='index'),
    url(r'^(?P<slug>[\w-]+)/$', PostDetailView.as_view(), name='detail'),
]
