from json import dumps

from django.test import TestCase
from django.utils.safestring import SafeText

from .templatetags.tojson import tojson
# from .tasks import send_slack_invite


class TestToJSONTemplateTag(TestCase):
    test_dict = {'foo': 'bar'}
    """Tests to validate that the tojson template tag correctly converts objects"""

    def test_converts_dict_to_safe_string(self):
        """ Basic dictionary conversion"""
        result = tojson(self.test_dict)
        self.assertEqual(result, dumps(self.test_dict))
        self.assertIsInstance(result, SafeText)
