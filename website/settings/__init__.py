import os as _os

_env = _os.getenv('PY_ENV')
if _env == 'development':
    from .development import *  # noqa
elif _env == 'testing':
    from .testing import *  # noqa
elif _env == 'production':
    from .production import *  # noqa
else:
    raise SystemExit('PY_ENV must be set to one of '
                     'development|testing|production')
