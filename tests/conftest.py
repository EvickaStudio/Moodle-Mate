"""Shared test fixtures and configuration."""

import logging
import os
import sys
from typing import Generator
from unittest.mock import Mock

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(autouse=True)
def setup_logging() -> Generator[None, None, None]:
    """Configure logging for tests."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    yield
    logging.getLogger().handlers.clear()


@pytest.fixture(autouse=True)
def reset_singletons() -> Generator[None, None, None]:
    """Reset global/singleton state between tests to avoid cross-test leakage."""
    try:
        from src.core.notification.processor import NotificationProcessor
        from src.core.config.loader import Config
        from src.core.service_locator import ServiceLocator
        from src.infrastructure.http.request_manager import (
            RequestManager,
            request_manager,
        )
    except Exception:
        NotificationProcessor = None  # type: ignore
        Config = None  # type: ignore
        ServiceLocator = None  # type: ignore
        RequestManager = None  # type: ignore
        request_manager = None  # type: ignore

    if NotificationProcessor is not None:
        NotificationProcessor._instance = None
    if Config is not None:
        Config._instance = None
    if ServiceLocator is not None:
        ServiceLocator._services.clear()
    if RequestManager is not None:
        RequestManager._instance = None
        RequestManager._default_timeout = (10, 30)
        RequestManager._retry_total = 3
        RequestManager._backoff_factor = 1.0
        if request_manager is not None:
            request_manager._default_timeout = (10, 30)
            request_manager._retry_total = 3
            request_manager._backoff_factor = 1.0
            request_manager._setup_session()

    yield

    if NotificationProcessor is not None:
        NotificationProcessor._instance = None
    if Config is not None:
        Config._instance = None
    if ServiceLocator is not None:
        ServiceLocator._services.clear()
    if RequestManager is not None:
        RequestManager._instance = None
        RequestManager._default_timeout = (10, 30)
        RequestManager._retry_total = 3
        RequestManager._backoff_factor = 1.0
        if request_manager is not None:
            request_manager._default_timeout = (10, 30)
            request_manager._retry_total = 3
            request_manager._backoff_factor = 1.0
            request_manager._setup_session()


@pytest.fixture
def mock_config() -> Mock:
    """Create a base mock configuration."""
    config = Mock()
    config.get_config.return_value = None
    return config
