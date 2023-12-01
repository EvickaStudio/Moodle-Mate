import logging


def handle_exceptions(func):
    """
    Decorator to handle exceptions in a standardized way across methods.
    Logs the exception and returns None in case of an error.

    :param func: The function to decorate.
    :return: Wrapped function with exception handling.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.exception(f"Exception occurred in {func.__name__}")
            return None

    return wrapper
