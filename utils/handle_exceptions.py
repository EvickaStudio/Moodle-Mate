import logging
import sys
import traceback

logger = logging.getLogger(__name__)


def handle_exceptions(func):
    """
    Decorator to handle exceptions in a standardized way across methods.
    Logs the exception and returns None in case of an error.

    :param func: The function to decorate.
    :return: Wrapped function with exception handling.
    """

    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except BaseException as e:
            logger.exception(f"Exception occurred in {func.__name__}: {str(e)}")
            _, err, tb = sys.exc_info()
            logger.debug(traceback.format_tb(err.__traceback__)[-1])
            return None
        else:
            return result

    return wrapper
