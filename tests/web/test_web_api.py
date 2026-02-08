import httpx
import pytest

from moodlemate.config import Settings
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
    def __init__(self) -> None:
        self.test_notifications_sent = 0

    def send_test_notification(self) -> None:
        self.test_notifications_sent += 1


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def settings() -> Settings:
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
    app_instance = DummyAppInstance()
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
    with pytest.raises(ValueError, match="requires 'web.auth_secret'"):
        WebUI(settings, DummyStateManager(), DummyAppInstance())
