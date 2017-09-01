from json import dumps

from django.utils.safestring import SafeText

from .templatetags.tojson import tojson


class TestToJSONTemplateTag:
    test_dict = {'foo': 'bar'}
    """Tests to validate that the tojson template tag correctly converts objects"""

    def test_converts_dict_to_safe_string(self):
        """Basic dictionary conversion"""
        result = tojson(self.test_dict)
        assert result == dumps(self.test_dict)
        assert isinstance(result, SafeText)
