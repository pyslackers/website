import contextvars

from uuid import uuid4

REQUEST_CONTEXT = contextvars.ContextVar("REQUEST_CONTEXT", default=uuid4())
