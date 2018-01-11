import os
import json

from app.marketing.views import version


class TestVersionView:
    """"Test case for verison API"""

    def test_no_app_version(self, rf):
        os.environ['APP_GIT_VERSION'] = ''
        request = rf.get('/version')
        response = version(request)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['revision'] == ''

    def test_app_version(self, rf):
        commit_sha = 'b0dca52c215f8384c94c4930ca9b9957d824c202'
        os.environ['APP_GIT_REVISION'] = commit_sha
        request = rf.get('/version')
        response = version(request)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['revision'] == commit_sha
