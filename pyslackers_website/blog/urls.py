from django.urls import path

from .views import LatestPostFeed, PostDetailView, PostListView


app_name = 'blog'

urlpatterns = [
    path('feed/', LatestPostFeed()),
    path('', PostListView.as_view(), name='index'),
    path('<slug:slug>/', PostDetailView.as_view(), name='detail'),
]
