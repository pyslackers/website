import os as _os
import warnings as _warnings

_env = _os.getenv('PY_ENV')
if _env == 'development':
    from .development import *  # noqa
elif _env == 'testing':
    from .testing import *  # noqa
else:
    if not _env:
        _warnings.warn("No PY_ENV provided, defaulting to 'production' for "
                       "safety.")
    from .production import *  # noqa
