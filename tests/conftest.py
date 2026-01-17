"""Shared test fixtures and configuration."""

import logging
from collections.abc import Generator
from unittest.mock import Mock

import pytest


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
        from moodlemate.infrastructure.http.request_manager import (
            RequestManager,
            request_manager,
        )
        from moodlemate.notifications.processor import NotificationProcessor
    except Exception:
        NotificationProcessor = None  # type: ignore
        RequestManager = None  # type: ignore
        request_manager = None  # type: ignore

    if NotificationProcessor is not None:
        NotificationProcessor._instance = None
    if RequestManager is not None:
        RequestManager._instance = request_manager
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
    if RequestManager is not None:
        RequestManager._instance = request_manager
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
