"""Dependency injection container for Moodle Mate."""

import logging
from typing import Any, Dict, Type, TypeVar
from injector import Injector, Module, singleton, provider
import uuid

from src.core.config.loader import Config
from src.core.security import CredentialManager, InputValidator, RateLimiterManager
from src.infrastructure.http.request_manager import RequestManager
from src.services.moodle.api import MoodleAPI
from src.core.notification.processor import NotificationProcessor
from src.core.state_manager import StateManager

logger = logging.getLogger(__name__)
T = TypeVar("T")


class ApplicationModule(Module):
    """Dependency injection module for Moodle Mate."""

    @singleton
    @provider
    def provide_config(self) -> Config:
        """Provide configuration instance."""
        try:
            return Config()
        except Exception as e:
            logger.error(f"Failed to initialize configuration: {e}")
            raise

    @singleton
    @provider
    def provide_credential_manager(self) -> CredentialManager:
        """Provide credential manager instance."""
        return CredentialManager("moodle-mate")

    @singleton
    @provider
    def provide_input_validator(self) -> InputValidator:
        """Provide input validator instance."""
        return InputValidator()

    @singleton
    @provider
    def provide_rate_limiter_manager(self) -> RateLimiterManager:
        """Provide rate limiter manager instance."""
        return RateLimiterManager()

    @singleton
    @provider
    def provide_request_manager(self) -> RequestManager:
        """Provide request manager instance."""
        return RequestManager()

    @singleton
    @provider
    def provide_moodle_api(
        self,
        config: Config,
        credential_manager: CredentialManager,
        input_validator: InputValidator,
        rate_limiter_manager: RateLimiterManager,
    ) -> MoodleAPI:
        """Provide Moodle API instance."""
        try:
            # Create non-singleton instance by calling constructor directly
            return MoodleAPI.__new__(MoodleAPI)
        except Exception as e:
            logger.error(f"Failed to initialize Moodle API: {e}")
            raise

    @singleton
    @provider
    def provide_state_manager(self) -> StateManager:
        """Provide state manager instance."""
        try:
            return StateManager()
        except Exception as e:
            logger.error(f"Failed to initialize state manager: {e}")
            raise

    @provider
    def provide_notification_processor(
        self,
        config: Config,
        # This would need to be populated with actual providers
    ) -> NotificationProcessor:
        """Provide notification processor instance."""
        try:
            # For now, initialize with empty provider list
            # This will be populated dynamically during application startup
            return NotificationProcessor.__new__(NotificationProcessor)
        except Exception as e:
            logger.error(f"Failed to initialize notification processor: {e}")
            raise


class ApplicationContainer:
    """Application-level dependency injection container."""

    def __init__(self):
        """Initialize the dependency injection container."""
        self._injector = Injector([ApplicationModule()])
        self._request_scopes: Dict[str, Any] = {}

    def get(self, service_type: Type[T]) -> T:
        """Get a service instance from the container.

        Args:
            service_type: Type of service to retrieve

        Returns:
            Service instance

        Raises:
            DependencyError: If service cannot be resolved
        """
        try:
            return self._injector.get(service_type)
        except Exception as e:
            correlation_id = str(uuid.uuid4())[:8]
            logger.error(
                f"Failed to resolve service {service_type.__name__} [{correlation_id}]: {e}"
            )
            from src.core.exceptions import DependencyError

            raise DependencyError(
                f"Cannot resolve service {service_type.__name__}",
                correlation_id=correlation_id,
                service_type=service_type.__name__,
            )

    def create_scoped(self, scope_id: str = None) -> "ScopedContainer":
        """Create a scoped container for request-scoped services.

        Args:
            scope_id: Optional scope identifier

        Returns:
            Scoped container instance
        """
        if scope_id is None:
            scope_id = str(uuid.uuid4())

        return ScopedContainer(self, scope_id)

    def register_instance(self, instance: Any, interface: Type = None) -> None:
        """Register an existing instance in the container.

        Args:
            instance: Instance to register
            interface: Interface type to register under
        """
        try:
            if interface is None:
                interface = type(instance)

            # Create a simple provider for the instance
            def provider_func():
                return instance

            # Register the provider
            self._injector.binder.bind(interface, to=provider_func)
            logger.info(f"Registered instance of {interface.__name__}")
        except Exception as e:
            logger.error(f"Failed to register instance: {e}")
            raise


class ScopedContainer:
    """Scoped container for request-scoped services."""

    def __init__(self, parent: ApplicationContainer, scope_id: str):
        """Initialize scoped container.

        Args:
            parent: Parent container
            scope_id: Scope identifier
        """
        self._parent = parent
        self._scope_id = scope_id
        self._scoped_instances: Dict[Type, Any] = {}

    def get(self, service_type: Type[T]) -> T:
        """Get a service instance from the container.

        Args:
            service_type: Type of service to retrieve

        Returns:
            Service instance
        """
        # Return scoped instances if available
        if service_type in self._scoped_instances:
            return self._scoped_instances[service_type]

        # Otherwise, get from parent container
        return self._parent.get(service_type)

    def register_scoped(self, instance: Any, interface: Type = None) -> None:
        """Register a scoped instance.

        Args:
            instance: Instance to register
            interface: Interface type to register under
        """
        if interface is None:
            interface = type(instance)

        self._scoped_instances[interface] = instance
        logger.debug(
            f"Registered scoped instance of {interface.__name__} for scope {self._scope_id}"
        )


# Global application container
application_container = ApplicationContainer()


def get_service(service_type: Type[T]) -> T:
    """Convenience function to get a service from the global container.

    Args:
        service_type: Type of service to retrieve

    Returns:
        Service instance
    """
    return application_container.get(service_type)


def create_scoped_service(scope_id: str = None) -> ScopedContainer:
    """Create a scoped container.

    Args:
        scope_id: Optional scope identifier

    Returns:
        Scoped container instance
    """
    return application_container.create_scoped(scope_id)


def initialize_dependencies(config: Config = None) -> None:
    """Initialize all dependencies and register them in the container.

    Args:
        config: Optional configuration to use
    """
    try:
        logger.info("Initializing application dependencies...")

        # Initialize configuration first
        if config is not None:
            application_container.register_instance(config)

        # Initialize and verify core services
        services_to_verify = [
            Config,
            CredentialManager,
            InputValidator,
            RateLimiterManager,
            RequestManager,
            StateManager,
        ]

        for service_type in services_to_verify:
            try:
                get_service(service_type)
                logger.debug(f"Initialized {service_type.__name__}")
            except Exception as e:
                logger.error(f"Failed to initialize {service_type.__name__}: {e}")
                raise

        logger.info("All dependencies initialized successfully")

    except Exception as e:
        correlation_id = str(uuid.uuid4())[:8]
        logger.error(f"Failed to initialize dependencies [{correlation_id}]: {e}")
        from src.core.exceptions import DependencyError

        raise DependencyError(
            "Failed to initialize application dependencies",
            correlation_id=correlation_id,
        )
