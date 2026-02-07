from moodlemate.infrastructure.http.request_manager import (
    RequestManager,
    request_manager,
)


def test_singleton_and_headers():
    rm1 = RequestManager()
    rm2 = RequestManager()
    assert rm1 is rm2

    headers = rm1.session.headers
    assert "User-Agent" in headers
    assert "MoodleMate" in headers["User-Agent"]

    rm1.update_headers({"X-Test": "1"})
    assert rm1.session.headers["X-Test"] == "1"


def test_reset_session_creates_new_instance():
    rm = RequestManager()
    session_before = rm.session
    rm.reset_session()
    session_after = rm.session
    assert session_before is not session_after


def test_global_instance():
    assert request_manager.session is RequestManager().session


def test_configure_updates_timeouts_and_retries():
    rm = RequestManager()
    rm.configure(connect_timeout=5, read_timeout=12, retry_total=2, backoff_factor=0.5)
    assert rm._default_timeout == (5, 12)
    assert rm._retry_total == 2
    assert rm._backoff_factor == 0.5


def test_scoped_sessions_isolate_state():
    rm = RequestManager()
    moodle = rm.get_session("moodle_test")
    provider = rm.get_session("provider_test")

    moodle.headers["Authorization"] = "Bearer moodle-token"
    moodle.cookies.set("moodle", "cookie", domain="moodle.example.com")

    assert "Authorization" not in provider.headers
    assert provider.cookies.get("moodle") is None


def test_retry_does_not_include_post():
    rm = RequestManager()
    adapter = rm.session.get_adapter("https://")
    assert "POST" not in adapter.max_retries.allowed_methods
