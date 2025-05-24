from typing import ClassVar, TypeVar

T = TypeVar("T")


class ServiceLocator:
    """
    A simple singleton implementation of the Service Locator pattern.

    This class provides a central registry for application services (singletons).
    It allows services to be registered with a unique name and later retrieved by
    that name, ensuring that only one instance of each service exists and is used
    throughout the application.

    The `ServiceLocator` itself is a singleton, ensuring that all parts of the
    application access the same registry of services.

    Key methods:
    - `register(service_name: str, service: object)`: To add a service instance.
    - `get(service_name: str, service_type: type[T])`: To retrieve a service instance,
      with type checking.

    Example:
        >>> class MyService:
        ...     def do_something(self):
        ...         return "Done!"
        >>>
        >>> # Initialization phase (e.g., in main.py or a services module)
        >>> locator = ServiceLocator()
        >>> my_service_instance = MyService()
        >>> locator.register("my_service", my_service_instance)
        >>>
        >>> # Usage phase (elsewhere in the application)
        >>> same_locator = ServiceLocator() # Gets the same instance
        >>> retrieved_service = same_locator.get("my_service", MyService)
        >>> print(retrieved_service.do_something())
        Done!
    """

    _instance = None
    _services: ClassVar[dict[str, object]] = {}

    def __new__(cls) -> "ServiceLocator":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, service_name: str, service: object) -> None:
        """
        Register a service instance with a unique name.

        If a service with the same name is already registered, it will be overwritten.

        Args:
            service_name (str): The unique name to identify the service.
            service (object): The instance of the service to register.

        Raises:
            TypeError: If `service_name` is not a string or `service` is None.
            ValueError: If `service_name` is an empty string.
        """
        if not isinstance(service_name, str):
            raise TypeError("service_name must be a string.")
        if not service_name:
            raise ValueError("service_name must not be empty.")
        if service is None:
            raise TypeError("service cannot be None.")

        cls._services[service_name] = service

    @classmethod
    def get(cls, service_name: str, service_type: type[T]) -> T:
        """
        Retrieve a registered service by its name, with type checking.

        Args:
            service_name (str): The unique name of the service to retrieve.
            service_type (type[T]): The expected type of the service. This is used
                for runtime type checking to ensure the retrieved service is
                of the correct class.

        Returns:
            T: The instance of the registered service, cast to `service_type`.

        Raises:
            KeyError: If no service is registered with the given `service_name`.
            TypeError: If the registered service is not an instance of `service_type`,
                       or if `service_name` is not a string, or `service_type` is not a type.
            ValueError: If `service_name` is an empty string.
        """
        if not isinstance(service_name, str):
            raise TypeError("service_name must be a string.")
        if not service_name:
            raise ValueError("service_name must not be empty.")
        if not isinstance(service_type, type):
            raise TypeError("service_type must be a type.")

        service = cls._services.get(service_name)
        if service is None:
            raise KeyError(f"Service not registered: {service_name}")
        if not isinstance(service, service_type):
            raise TypeError(f"Service {service_name} is not of type {service_type}")
        return service
