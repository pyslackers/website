from logging import LoggerAdapter

from .context import REQUEST_CONTEXT


class ContextAwareLoggerAdapter(LoggerAdapter):
    """
    Logging adapter to attach the request context to logs, if
    set.
    """

    def __init__(self, logger, extra=None):
        super().__init__(logger, extra or {})

    def process(self, msg, kwargs):
        context_id = REQUEST_CONTEXT.get(None)
        if context_id:
            return f"[{context_id}] {msg}", kwargs
        return msg, kwargs
