from django.contrib.auth import get_user_model
from django.http.response import Http404
from django.utils import timezone

import pytest

from .models import Post, Tag
from .views import PostDetailView, PostListView

User = get_user_model()


@pytest.mark.django_db
class TestPostListView:
    def test_no_posts(self, rf):
        request = rf.get('/blog/')
        response = PostListView.as_view()(request)
        assert response.status_code == 200
        assert response.context_data['posts'].count() == 0

    def test_posts_with_no_tags(self, rf, admin_user):
        Post.objects.bulk_create([
            Post(title='First', content='# First Content',
                 published_at=timezone.now(), author=admin_user),
            Post(title='Second', content='# Second Content',
                 published_at=timezone.now(), author=admin_user),
            Post(title='Third', content='# Third Content',
                 author=admin_user),
        ])
        response = PostListView.as_view()(rf.get('/blog/'))
        assert response.status_code == 200
        assert response.context_data['posts'].count() == 2

    def test_posts_with_tags(self, rf, admin_user):
        tags = Tag.objects.bulk_create([
            Tag(name='foo'),
            Tag(name='bar'),
            Tag(name='baz'),
        ])

        posts = Post.objects.bulk_create([
            Post(title='First', content='# First Content',
                 published_at=timezone.now(), author=admin_user),
            Post(title='Second', content='# Second Content',
                 published_at=timezone.now(), author=admin_user),
            Post(title='Third', content='# Third Content',
                 published_at=timezone.now(), author=admin_user),
        ])
        posts[0].tags.add(tags[0])
        posts[0].tags.add(tags[1])
        posts[1].tags.add(tags[1])

        response = PostListView.as_view()(rf.get('/blog/'))
        assert response.status_code == 200
        assert response.context_data['posts'].count() == 3
        assert response.context_data['tags'].count() == 2

    def test_tags_with_no_posts(self, rf):
        Tag.objects.bulk_create([
            Tag(name='foo'),
            Tag(name='bar'),
            Tag(name='baz')
        ])

        response = PostListView.as_view()(rf.get('/blog/'))
        assert response.status_code == 200
        assert response.context_data['posts'].count() == 0
        assert response.context_data['tags'].count() == 0


class TestPostDetailView:
    @pytest.mark.django_db
    def test_missing_post(self, rf):
        with pytest.raises(Http404):
            request = rf.get('/blog/foo-bar/')
            PostDetailView.as_view()(request, slug='foo-bar')

    @pytest.mark.django_db
    def test_found_post(self, rf, admin_user):
        post1 = Post(title='First', content='# First Content',
                     published_at=timezone.now(), author=admin_user)
        post1.save()

        request = rf.get(f'/blog/{post1.slug}/')
        response = PostDetailView.as_view()(request, slug=post1.slug)
        assert response.status_code == 200


class TestPostModel:

    def test_post_str(self, admin_user):
        post1 = Post(title='First', content='# First Content',
                     published_at=timezone.now(), author=admin_user)
        assert str(post1) == post1.title

    def test_post_slug_set_once(self, admin_user):
        post1 = Post(title='First One', content='# First Content',
                     published_at=timezone.now(), author=admin_user)
        post1.save()
        assert post1.slug == 'first-one'

        post1.title = 'Changed'
        post1.save()
        assert post1.slug == 'first-one'


class TestTagModel:

    def test_tag_str(self):
        tag = Tag(name='Foo')
        assert str(tag) == tag.name

    @pytest.mark.django_db
    def test_name_lowered_on_save(self):
        tag = Tag(name='Foo')
        tag.save()

        assert tag.name == 'foo'
