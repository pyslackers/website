import contextvars


REQUEST_CONTEXT = contextvars.ContextVar("REQUEST_CONTEXT", default=None)
