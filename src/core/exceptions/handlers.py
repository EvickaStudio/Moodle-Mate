from collections.abc import Callable
import logging
import traceback
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


def handle_exceptions(func: Callable[..., Any | None]) -> Callable[..., Any | None]:
    """
    Decorator to handle exceptions in a standardized way across methods.
    Logs the exception and returns None in case of an error.

    Args:
        func: The function to decorate.
    Returns:
        Wrapped function with exception handling.
    """

    def wrapper(*args: Any, **kwargs: Any) -> Any | None:
        """
        Wrapper function to execute the decorated function and handle exceptions.
        Logs exceptions and returns None in case of an error.

        Args:
            *args: Arguments passed to the decorated function.
            **kwargs: Keyword arguments passed to the decorated function.
        Returns:
            The result of the decorated function or None if an exception occurred.
        """
        try:
            result = func(*args, **kwargs)
        except BaseException as e:
            logger.exception(f"Exception occurred in {func.__name__}: {e!s}")
            tb = traceback.extract_tb(e.__traceback__)
            logger.debug(tb[-1])
            return None
        else:
            return result

    return wrapper
