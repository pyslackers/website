"""
blog/views
"""
from django.views.generic import DetailView, ListView

from .models import Post, Tag


class PostIndex(ListView):
    """PostIndex"""
    model = Post
    context_object_name = 'posts'

    def get_queryset(self):
        """get_queryset"""
        query = super(PostIndex, self).get_queryset()\
            .order_by('-published_at')\
            .filter(published_at__isnull=False)
        tag_filter = self.request.GET.get('tag')
        if tag_filter:
            query = query.filter(tags__name=tag_filter)
        return query

    def get_context_data(self, **kwargs):
        """get_context_data"""
        context = super(PostIndex, self).get_context_data(**kwargs)
        context['tags'] = Tag.objects.order_by('name').all()
        return context


class PostDetail(DetailView):
    """PostDetail"""
    model = Post
    context_object_name = 'post'
