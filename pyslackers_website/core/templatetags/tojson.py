""" This module provides a Django template tag to convert objects to JSON strings via the builtin json.dumps. """

import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def tojson(value, *args, **kwargs):
    """Converts the given value to a JSON string, takes additional arguments as per json.dumps"""
    return mark_safe(json.dumps(value, *args, **kwargs))
