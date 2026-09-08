import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock

import httpx
import pytest

from moodlemate.ai.chat import GPT
from moodlemate.app import MoodleMateApp
from moodlemate.config import Settings
from moodlemate.core.security.rate_limiter import RateLimiterManager
from moodlemate.notifications.processor import NotificationProcessor
from moodlemate.notifications.summarizer import NotificationSummarizer
from moodlemate.providers.notification import initialize_providers
from moodlemate.web.api import CSRF_COOKIE_NAME, CSRF_HEADER_NAME, WebUI


class DummyStateManager:
    def __init__(self) -> None:
        self.last_notification_id = 77
        self._history = [
            {
                "id": 77,
                "subject": "Hello",
                "message": "Body",
                "providers": ["discord"],
                "timestamp": 1700000000,
            }
        ]

    def get_history(self) -> list[dict]:
        return list(self._history)


class DummyAppInstance:
    def __init__(self, settings=None) -> None:
        self.test_notifications_sent = 0
        self.settings = settings

    def apply_settings(self, settings) -> None:
        for field in settings.__class__.model_fields:
            setattr(self.settings, field, getattr(settings, field))

    def send_test_notification(self) -> None:
        self.test_notifications_sent += 1

    def get_health_status(self) -> tuple[bool, dict[str, object]]:
        return True, {"status": "ok", "last_successful_poll": 123.0}


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def settings(monkeypatch) -> Settings:
    monkeypatch.setattr("moodlemate.web.api.rate_limiter_manager", RateLimiterManager())
    return Settings(
        _env_file=None,
        moodle={
            "url": "https://moodle.example.edu",
            "username": "alice",
            "password": "supersecret",
            "initial_fetch_count": 2,
        },
        ai={"enabled": True, "api_key": "sk-" + ("a" * 48)},
        web={"enabled": True, "host": "127.0.0.1", "port": 9095, "auth_secret": "pw"},
        discord={"enabled": True, "webhook_url": "https://discord.example/webhook"},
        pushbullet={"enabled": True, "api_key": "pb-secret"},
        webhook_site={"enabled": True, "webhook_url": "https://webhook.site/test"},
    )


@pytest.fixture
def webui(settings: Settings) -> tuple[WebUI, DummyAppInstance]:
    state_manager = DummyStateManager()
    app_instance = DummyAppInstance(settings)
    return WebUI(settings, state_manager, app_instance), app_instance


@pytest.fixture
async def client(webui: tuple[WebUI, DummyAppInstance]) -> httpx.AsyncClient:
    ui, _ = webui
    transport = httpx.ASGITransport(app=ui.get_app())
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as async_client:
        yield async_client


async def _login(client: httpx.AsyncClient, password: str = "pw") -> None:
    await client.get("/login")
    csrf_token = client.cookies.get(CSRF_COOKIE_NAME)
    assert csrf_token

    response = await client.post(
        "/api/login",
        json={"password": password},
        headers={CSRF_HEADER_NAME: csrf_token},
    )
    assert response.status_code == 200


def _csrf_headers(client: httpx.AsyncClient) -> dict[str, str]:
    token = client.cookies.get(CSRF_COOKIE_NAME)
    assert token
    return {CSRF_HEADER_NAME: token}


@pytest.mark.anyio
async def test_protected_route_requires_authentication(client: httpx.AsyncClient):
    response = await client.get("/api/status")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_health_endpoint_reports_runtime_health(client: httpx.AsyncClient):
    response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["last_successful_poll"] == 123.0


@pytest.mark.anyio
async def test_login_page_is_self_contained_and_static(client: httpx.AsyncClient):
    response = await client.get("/login")

    assert response.status_code == 200
    assert "cdn.tailwindcss.com" not in response.text
    assert "unpkg.com" not in response.text
    assert "animation:" not in response.text
    assert "transition:" not in response.text


@pytest.mark.anyio
async def test_login_requires_csrf_token(client: httpx.AsyncClient):
    response = await client.post("/api/login", json={"password": "pw"})
    assert response.status_code == 403


@pytest.mark.anyio
async def test_login_with_invalid_password_keeps_client_unauthenticated(
    client: httpx.AsyncClient,
):
    await client.get("/login")
    csrf_token = client.cookies.get(CSRF_COOKIE_NAME)
    assert csrf_token

    login_response = await client.post(
        "/api/login",
        json={"password": "wrong-password"},
        headers={CSRF_HEADER_NAME: csrf_token},
    )
    assert login_response.status_code == 401

    status_response = await client.get("/api/status")
    assert status_response.status_code == 401


@pytest.mark.anyio
async def test_authenticated_user_can_fetch_status_history_and_config(
    client: httpx.AsyncClient,
):
    await _login(client)

    dashboard = await client.get("/")
    assert dashboard.status_code == 200
    assert "cdn.tailwindcss.com" not in dashboard.text
    assert "unpkg.com" not in dashboard.text
    assert "animation:" not in dashboard.text
    assert "transition:" not in dashboard.text
    assert "Recent activity" in dashboard.text
    assert "Runtime settings" in dashboard.text
    assert 'href="#overview"' not in dashboard.text
    assert '<details class="settings">' not in dashboard.text

    status = await client.get("/api/status")
    history = await client.get("/api/history")
    config = await client.get("/api/config")

    assert status.status_code == 200
    assert status.json()["last_notification_id"] == 77
    assert history.status_code == 200
    assert len(history.json()) == 1
    assert config.status_code == 200
    config_payload = config.json()
    assert config_payload["moodle"]["password"] == "********"
    assert config_payload["ai"]["api_key"] == "********"
    assert config_payload["discord"]["webhook_url"] == "********"


@pytest.mark.anyio
async def test_config_update_keeps_immutable_fields(
    client: httpx.AsyncClient, settings: Settings
):
    await _login(client)
    original_moodle_url = settings.moodle.url

    response = await client.post(
        "/api/config",
        json={
            "moodle": {"url": "https://evil.invalid"},
            "notification": {"fetch_interval": 123},
            "health": {"enabled": True, "target_provider": "discord"},
        },
        headers=_csrf_headers(client),
    )

    assert response.status_code == 200
    assert settings.moodle.url == original_moodle_url
    assert settings.notification.fetch_interval == 123
    assert settings.health.enabled is True
    assert settings.health.target_provider == "discord"


@pytest.mark.anyio
async def test_config_update_changes_actual_delivery_components(settings, monkeypatch):
    monkeypatch.setattr(GPT, "_instance", None)
    gpt = GPT()
    monkeypatch.setattr(gpt, "chat_completion", Mock(return_value="Updated summary"))
    state = Mock()
    state.get_delivered_providers.return_value = set()
    processor = NotificationProcessor(
        settings,
        initialize_providers(settings),
        state,
        NotificationSummarizer(settings, gpt),
    )
    app = MoodleMateApp(settings, processor, Mock(), Mock(), state)
    ui = WebUI(settings, state, app)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=ui.get_app()), base_url="http://testserver"
    ) as client:
        await _login(client)
        response = await client.post(
            "/api/config",
            headers=_csrf_headers(client),
            json={
                "ai": {"enabled": False},
                "discord": {"enabled": False},
                "pushbullet": {"enabled": False},
                "webhook_site": {"include_summary": False},
                "notification": {"read_timeout": 14},
            },
        )
        assert response.status_code == 200
        assert [provider.provider_name for provider in processor.providers] == [
            "webhook_site"
        ]
        assert processor.providers[0].include_summary is False
        assert processor.providers[0].session._default_timeout[1] == 14
        assert processor.summarizer is None

        response = await client.post(
            "/api/config",
            headers=_csrf_headers(client),
            json={
                "ai": {
                    "enabled": True,
                    "model": "updated-model",
                    "temperature": 0.2,
                    "max_tokens": 77,
                },
                "discord": {"enabled": True, "bot_name": "Updated bot"},
                "webhook_site": {"enabled": False},
            },
        )
        assert response.status_code == 200
        provider = processor.providers[0]
        assert provider.provider_name == "discord"
        monkeypatch.setattr(
            provider.session, "post", Mock(return_value=Mock(status_code=204))
        )
        app.send_test_notification()
        assert gpt.chat_completion.call_args.kwargs["model"] == "updated-model"
        assert gpt.chat_completion.call_args.kwargs["temperature"] == 0.2
        assert gpt.chat_completion.call_args.kwargs["max_tokens"] == 77
        payload = provider.session.post.call_args.kwargs["json"]
        assert payload["username"] == "Updated bot"
        assert payload["embeds"][0]["fields"][0]["value"] == "Updated summary"

        old_settings = settings.model_dump()
        old_providers = processor.providers
        response = await client.post(
            "/api/config",
            headers=_csrf_headers(client),
            json={
                "discord": {"enabled": False},
                "notification": {"read_timeout": -1},
            },
        )
        assert response.status_code == 400
        assert settings.model_dump() == old_settings
        assert processor.providers is old_providers

        monkeypatch.setattr(
            "moodlemate.app.initialize_providers",
            Mock(side_effect=ValueError("Provider configuration is invalid")),
        )
        response = await client.post(
            "/api/config",
            headers=_csrf_headers(client),
            json={"discord": {"bot_name": "Not applied"}},
        )
        assert response.status_code == 500
        assert settings.model_dump() == old_settings
        assert processor.providers is old_providers


def test_settings_update_waits_for_active_delivery(settings, monkeypatch):
    delivering = threading.Event()
    release_delivery = threading.Event()
    update_started = threading.Event()
    configured = threading.Event()

    def deliver(_notification):
        delivering.set()
        assert release_delivery.wait(timeout=5)
        return Mock(delivered=True)

    def create_providers(_settings):
        configured.set()
        return []

    processor = Mock()
    processor.process.side_effect = deliver
    app = MoodleMateApp(settings, processor, Mock(), Mock(), Mock())
    monkeypatch.setattr("moodlemate.app.initialize_providers", create_providers)
    monkeypatch.setattr("moodlemate.app.initialize_summarizer", Mock(return_value=None))

    def update():
        update_started.set()
        app.apply_settings(settings.model_copy(deep=True))

    with ThreadPoolExecutor(max_workers=2) as pool:
        delivery = pool.submit(app.send_test_notification)
        try:
            assert delivering.wait(timeout=5)
            updating = pool.submit(update)
            assert update_started.wait(timeout=5)
            assert not configured.wait(timeout=0.05)
        finally:
            release_delivery.set()
        delivery.result(timeout=5)
        updating.result(timeout=5)
    assert configured.is_set()


@pytest.mark.anyio
async def test_test_notification_endpoint_triggers_app_instance(
    client: httpx.AsyncClient, webui: tuple[WebUI, DummyAppInstance]
):
    _, app_instance = webui
    await _login(client)

    response = await client.post(
        "/api/test-notification",
        headers=_csrf_headers(client),
    )

    assert response.status_code == 200
    assert app_instance.test_notifications_sent == 1


@pytest.mark.anyio
async def test_logout_invalidates_session(client: httpx.AsyncClient):
    await _login(client)
    assert (await client.get("/api/status")).status_code == 200

    response = await client.post("/api/logout", headers=_csrf_headers(client))
    assert response.status_code == 200
    assert (await client.get("/api/status")).status_code == 401


def test_webui_refuses_to_start_without_auth_secret(settings: Settings):
    settings.web.auth_secret = None
    with pytest.raises(ValueError, match=r"requires 'web.auth_secret'"):
        WebUI(settings, DummyStateManager(), DummyAppInstance())
