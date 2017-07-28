import os as _os
import sys as _sys
import warnings as _warnings

_env = _os.getenv('PY_ENV')
if _env == 'testing' or 'test' in _sys.argv:
    from .testing import *  # noqa
elif _env == 'development':
    from .development import *  # noqa
else:
    if not _env:
        _warnings.warn("No PY_ENV provided, defaulting to 'production' for "
                       "safety.")
    from .production import *  # noqa
