from django.contrib.auth import get_user_model
from django.http.response import Http404
from django.utils import timezone
from django.test import RequestFactory, TestCase

from .models import Post, Tag
from .views import PostDetailView, PostListView

User = get_user_model()


class TestPostListView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='foo',
                                             email='foo@gmail.com',
                                             password='baz')
        self.factory = RequestFactory()

    def test_no_posts(self):
        request = self.factory.get('/blog/')
        response = PostListView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['posts'].count(), 0)

    def test_posts_with_no_tags(self):
        Post.objects.bulk_create([
            Post(title='First', content='# First Content',
                 published_at=timezone.now(), author=self.user),
            Post(title='Second', content='# Second Content',
                 published_at=timezone.now(), author=self.user),
            Post(title='Third', content='# Third Content',
                 author=self.user),
        ])
        request = self.factory.get('/blog/')
        response = PostListView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['posts'].count(), 2)

    def test_posts_with_tags(self):
        tag_foo = Tag(name='foo')
        tag_foo.save()
        tag_bar = Tag(name='bar')
        tag_bar.save()
        tag_baz = Tag(name='baz')
        tag_baz.save()

        post1 = Post(title='First', content='# First Content',
                     published_at=timezone.now(), author=self.user)
        post1.save()
        post1.tags.add(tag_foo)
        post1.tags.add(tag_bar)

        post2 = Post(title='Second', content='# Second Content',
                     published_at=timezone.now(), author=self.user)
        post2.save()
        post2.tags.add(tag_bar)

        post3 = Post(title='Third', content='# Third Content',
                     published_at=timezone.now(), author=self.user)
        post3.save()

        request = self.factory.get('/blog/')
        response = PostListView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['posts'].count(), 3)
        self.assertEqual(response.context_data['tags'].count(), 2)

    def test_tags_with_no_posts(self):
        tag_foo = Tag(name='foo')
        tag_foo.save()
        tag_bar = Tag(name='bar')
        tag_bar.save()
        tag_baz = Tag(name='baz')
        tag_baz.save()

        request = self.factory.get('/blog/')
        response = PostListView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['posts'].count(), 0)
        self.assertEqual(response.context_data['tags'].count(), 0)


class TestPostDetailView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='foo',
                                             email='foo@gmail.com',
                                             password='baz')
        self.factory = RequestFactory()

    def test_missing_post(self):
        with self.assertRaises(Http404):
            request = self.factory.get('/blog/foo-bar/')
            PostDetailView.as_view()(request, slug='foo-bar')

    def test_found_post(self):
        post1 = Post(title='First', content='# First Content',
                     published_at=timezone.now(), author=self.user)
        post1.save()

        request = self.factory.get(f'/blog/{post1.slug}/')
        response = PostDetailView.as_view()(request, slug=post1.slug)
        self.assertEqual(response.status_code, 200)
