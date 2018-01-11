#!/usr/bin/env python
import os
import pathlib
import sys

if __name__ == '__main__':
    if sys.version_info < (3, 6):
        raise SystemExit('This project uses features only in Python 3.6+, '
                         'please update your Python version.')

    os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                          'config.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django  # noqa
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise

    current_path = pathlib.Path(__file__).parent
    sys.path.append(str(current_path / 'app'))

    execute_from_command_line(sys.argv)
