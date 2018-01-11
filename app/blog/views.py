"""
blog/views
"""
from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.views.generic import DetailView, ListView

from .models import Post, Tag


class LatestPostFeed(Feed):
    title = 'PySlackers blog'
    link = '/blog/'
    description = 'Keep up-to-date with the PySlackers latest posts'

    def items(self):
        return Post.objects.published()[:5]

    def item_title(self, item: Post):
        return item.title

    def item_description(self, item: Post):
        return item.content[:255]

    def item_link(self, item: Post):
        return reverse('blog:detail', args=[item.slug])


class PostListView(ListView):
    """PostIndex"""
    model = Post
    context_object_name = 'posts'

    def get_queryset(self):
        """get_queryset"""
        query = Post.objects.published()
        tag_filter = self.request.GET.get('tag')
        if tag_filter:
            query = query.filter(tags__name=tag_filter)
        return query

    def get_context_data(self, **kwargs):
        """get_context_data"""
        context = super(PostListView, self).get_context_data(**kwargs)
        context['tags'] = Tag.objects.names()
        return context


class PostDetailView(DetailView):
    """PostDetail"""
    model = Post
    context_object_name = 'post'
