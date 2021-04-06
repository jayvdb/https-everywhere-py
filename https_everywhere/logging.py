__all__ = ("setup_logging",)

try:
    from logging_helper import setup_logging
except ImportError:
    from warnings import warn

    class LoggerMock:
        def info(self, *args, **kwargs):
            pass

        def debug(self, *args, **kwargs):
            pass

        def error(self, *args, **kwargs):
            pass

        def warning(self, *args, **kwargs):
            pass

    def setup_logging():
        warn("logging_helper is not available, no logging is set up")
        return LoggerMock()
