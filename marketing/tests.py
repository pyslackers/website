from unittest import mock

from django.test import TestCase
from requests import Response


from .tasks import get_github_repos, send_slack_invite


# class TestSendSlackInvite(TestCase):
#     @mock.patch('requests.post')
#     def test_sends(self, mocked_post):
#         mocked_post.return_value = Response()
#         send_slack_invite()


# class TestGithubTask(TestCase):
#     def setUp(self):
#         pass
#
#     def tearDown(self):
#         pass
#
#     @mock.patch('requests.get')
#     def test_sorts_by_stars(self, mocked_requests):
#         get_github_repos(org='foobar')
