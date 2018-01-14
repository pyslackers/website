from django import template
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static

register = template.Library()


class Settings:
    WEBPACK_ENABLED = getattr(settings, 'DEBUG', False)
    WEBPACK_HOST = getattr(settings, 'WEBPACK_HOST', 'http://localhost')
    WEBPACK_PORT = getattr(settings, 'WEBPACK_PORT', 8080)


@register.simple_tag
def static_webpack(path: str):
    """If debug is enabled, prepend the webpack-dev-server base-url to the
    request, otherwise return the relative static version."""
    prefix = ''
    if Settings.WEBPACK_ENABLED:
        prefix = f'{Settings.WEBPACK_HOST}:{Settings.WEBPACK_PORT}'
    return f'{prefix}{static(path)}'
