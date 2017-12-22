import os
import json

from .views import version


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
        COMMIT_SHA = 'b0dca52c215f8384c94c4930ca9b9957d824c202'
        os.environ['APP_GIT_REVISION'] = COMMIT_SHA
        request = rf.get('/version')
        response = version(request)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['revision'] == COMMIT_SHA
