import logging
import traceback
from functools import wraps


def log_exception(once: bool = False, level_log: int = logging.WARNING):
    def outer_wrapper(func: callable):
        @wraps(func)
        def inner_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if not(getattr(func, "_is_called", False) and once):
                    logging.log(level_log, f"Catch exception for function {func}")
                    logging.log(level_log, f"\tException message {repr(e)}")
                    logging.log(level_log, f"\tException traceback {repr(traceback.format_tb(e.__traceback__))}")
                func._is_called = True
                raise e

        return inner_wrapper

    return outer_wrapper
