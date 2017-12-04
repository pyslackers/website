from django.conf.urls import url

from .views import LatestPostFeed, PostDetailView, PostListView


app_name = 'blog'

urlpatterns = [
    url(r'^feed/$', LatestPostFeed()),
    url(r'^$', PostListView.as_view(), name='index'),
    url(r'^(?P<slug>[\w-]+)/$', PostDetailView.as_view(), name='detail'),
]
