import logging
import secrets
import time
from pathlib import Path
from typing import Any

from fastapi import Body, Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from moodlemate.config import Settings
from moodlemate.core.security import rate_limiter_manager
from moodlemate.core.state_manager import StateManager
from moodlemate.core.version import __version__
from moodlemate.infrastructure.http.request_manager import request_manager

logger = logging.getLogger(__name__)

COOKIE_NAME = "moodlemate_auth"
CSRF_COOKIE_NAME = "moodlemate_csrf"
CSRF_HEADER_NAME = "X-CSRF-Token"
COOKIE_MAX_AGE_SECONDS = 86400 * 30  # 30 days
LOGIN_BODY = Body(...)
CONFIG_BODY = Body(...)


class WebUI:
    """Web dashboard for inspecting status and safely managing runtime configuration."""

    def __init__(
        self, settings: Settings, state_manager: StateManager, app_instance: Any
    ) -> None:
        if not settings.web.auth_secret:
            raise ValueError(
                "Web UI requires 'web.auth_secret'. Refusing to start without authentication."
            )

        self.settings = settings
        self.state_manager = state_manager
        self.app_instance = app_instance
        self._active_sessions: dict[str, float] = {}

        self.app = FastAPI(title="Moodle Mate WebUI")
        base_dir = Path(__file__).resolve().parent
        self.app.mount(
            "/static",
            StaticFiles(directory=str(base_dir / "static")),
            name="static",
        )
        self.templates = Jinja2Templates(directory=str(base_dir / "templates"))

        self._setup_middleware()
        self._setup_routes()

    @staticmethod
    def _is_secure_request(request: Request) -> bool:
        forwarded_proto = (
            request.headers.get("x-forwarded-proto", "").split(",")[0].strip().lower()
        )
        return request.url.scheme == "https" or forwarded_proto == "https"

    def _setup_middleware(self) -> None:
        @self.app.middleware("http")
        async def csrf_cookie_middleware(request: Request, call_next: Any) -> Response:
            response = await call_next(request)
            csrf_cookie = request.cookies.get(CSRF_COOKIE_NAME)
            if not csrf_cookie:
                response.set_cookie(
                    key=CSRF_COOKIE_NAME,
                    value=secrets.token_urlsafe(32),
                    httponly=False,
                    max_age=COOKIE_MAX_AGE_SECONDS,
                    samesite="strict",
                    secure=self._is_secure_request(request),
                )
            return response

    def _prune_expired_sessions(self) -> None:
        now = time.time()
        expired_tokens = [
            token
            for token, expires_at in self._active_sessions.items()
            if expires_at < now
        ]
        for token in expired_tokens:
            self._active_sessions.pop(token, None)

    def _create_session_token(self) -> str:
        self._prune_expired_sessions()
        token = secrets.token_urlsafe(32)
        self._active_sessions[token] = time.time() + COOKIE_MAX_AGE_SECONDS
        return token

    def _invalidate_session_token(self, token: str | None) -> None:
        if token:
            self._active_sessions.pop(token, None)

    def _check_auth(self, request: Request) -> bool:
        """Check if the request contains a valid active session token."""
        self._prune_expired_sessions()

        cookie_value = request.cookies.get(COOKIE_NAME)
        if cookie_value is None:
            return False

        expires_at = self._active_sessions.get(str(cookie_value))
        return expires_at is not None and expires_at >= time.time()

    async def _auth_dependency(self, request: Request) -> None:
        """Dependency to protect authenticated API routes."""
        if not self._check_auth(request):
            raise HTTPException(status_code=401, detail="Unauthorized")

    async def _csrf_dependency(self, request: Request) -> None:
        """Dependency validating double-submit CSRF tokens for state-changing requests."""
        csrf_cookie = request.cookies.get(CSRF_COOKIE_NAME)
        csrf_header = request.headers.get(CSRF_HEADER_NAME)
        if (
            not csrf_cookie
            or not csrf_header
            or not secrets.compare_digest(str(csrf_cookie), str(csrf_header))
        ):
            raise HTTPException(status_code=403, detail="CSRF validation failed")

    @staticmethod
    def _redact_config(config_dict: dict[str, Any]) -> dict[str, Any]:
        redact_paths = [
            ("moodle", "password"),
            ("ai", "api_key"),
            ("web", "auth_secret"),
            ("discord", "webhook_url"),
            ("pushbullet", "api_key"),
            ("webhook_site", "webhook_url"),
        ]
        for section, key in redact_paths:
            section_data = config_dict.get(section)
            if isinstance(section_data, dict) and section_data.get(key):
                section_data[key] = "********"
        return config_dict

    @staticmethod
    def _is_immutable_config_path(path: tuple[str, ...]) -> bool:
        immutable_paths = {
            ("moodle", "url"),
            ("moodle", "username"),
            ("moodle", "password"),
            ("ai", "api_key"),
            ("ai", "endpoint"),
            ("web", "enabled"),
            ("web", "host"),
            ("web", "port"),
            ("web", "auth_secret"),
            ("discord", "webhook_url"),
            ("pushbullet", "api_key"),
            ("webhook_site", "webhook_url"),
        }
        return path in immutable_paths

    def _setup_routes(self) -> None:
        @self.app.get("/login", response_class=HTMLResponse)
        async def login_page(request: Request) -> Response:
            if self._check_auth(request):
                return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
            return self.templates.TemplateResponse("login.html", {"request": request})

        @self.app.post("/api/login", dependencies=[Depends(self._csrf_dependency)])
        async def login(
            request: Request, response: Response, payload: Any = LOGIN_BODY
        ) -> dict[str, str]:
            client_ip = request.client.host if request.client else "unknown"
            if not rate_limiter_manager.is_allowed("web_login", client_ip):
                raise HTTPException(
                    status_code=429,
                    detail="Too many login attempts. Please try again later.",
                )

            password = None
            if isinstance(payload, dict):
                password = payload.get("password")
            elif isinstance(payload, str):
                password = payload

            if password is None:
                raise HTTPException(status_code=400, detail="Password required")

            if not secrets.compare_digest(
                str(password), str(self.settings.web.auth_secret)
            ):
                raise HTTPException(status_code=401, detail="Invalid password")

            session_token = self._create_session_token()
            response.set_cookie(
                key=COOKIE_NAME,
                value=session_token,
                httponly=True,
                max_age=COOKIE_MAX_AGE_SECONDS,
                samesite="strict",
                secure=self._is_secure_request(request),
            )
            return {"message": "Logged in"}

        @self.app.post(
            "/api/logout",
            dependencies=[
                Depends(self._auth_dependency),
                Depends(self._csrf_dependency),
            ],
        )
        async def logout(request: Request, response: Response) -> dict[str, str]:
            self._invalidate_session_token(request.cookies.get(COOKIE_NAME))
            response.delete_cookie(COOKIE_NAME)
            return {"message": "Logged out"}

        @self.app.get("/", response_class=HTMLResponse)
        async def read_root(request: Request) -> Response:
            if not self._check_auth(request):
                return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

            return self.templates.TemplateResponse(
                "index.html", {"request": request, "version": __version__}
            )

        @self.app.get("/api/status", dependencies=[Depends(self._auth_dependency)])
        async def get_status() -> dict[str, Any]:
            return {
                "running": True,
                "last_notification_id": self.state_manager.last_notification_id,
            }

        @self.app.get("/healthz")
        async def healthz() -> dict[str, str]:
            return {"status": "ok"}

        @self.app.get("/api/history", dependencies=[Depends(self._auth_dependency)])
        async def get_history() -> list[dict]:
            return self.state_manager.get_history()

        @self.app.get("/api/config", dependencies=[Depends(self._auth_dependency)])
        async def get_config() -> dict[str, Any]:
            config_dict = self.settings.model_dump()
            return self._redact_config(config_dict)

        @self.app.post(
            "/api/config",
            dependencies=[
                Depends(self._auth_dependency),
                Depends(self._csrf_dependency),
            ],
        )
        async def update_config(
            new_config: dict[str, Any] = CONFIG_BODY,
        ) -> dict[str, str]:
            try:

                def merge_dict(
                    target: dict[str, Any],
                    updates: dict[str, Any],
                    path: tuple[str, ...] = (),
                ) -> None:
                    for key, value in updates.items():
                        if key not in target:
                            continue

                        current_path = (*path, key)
                        if self._is_immutable_config_path(current_path):
                            continue

                        if (
                            isinstance(value, dict)
                            and isinstance(target.get(key), dict)
                            and not self._is_immutable_config_path(current_path)
                        ):
                            merge_dict(target[key], value, current_path)
                        else:
                            if value == "********":
                                continue
                            target[key] = value

                current_config = self.settings.model_dump()
                merge_dict(current_config, new_config)

                try:
                    validated = Settings.model_validate(current_config)
                except ValidationError as exc:
                    raise HTTPException(status_code=400, detail=exc.errors()) from exc

                for field_name in validated.__class__.model_fields:
                    setattr(self.settings, field_name, getattr(validated, field_name))

                request_manager.configure(
                    connect_timeout=self.settings.notification.connect_timeout,
                    read_timeout=self.settings.notification.read_timeout,
                    retry_total=self.settings.notification.retry_total,
                    backoff_factor=self.settings.notification.retry_backoff_factor,
                )

                logger.info("Configuration updated via WebUI")
                return {"message": "Configuration updated successfully."}

            except HTTPException:
                raise
            except Exception:
                logger.exception("Failed to update config")
                raise HTTPException(
                    status_code=500, detail="Internal server error"
                ) from None

        @self.app.post(
            "/api/test-notification",
            dependencies=[
                Depends(self._auth_dependency),
                Depends(self._csrf_dependency),
            ],
        )
        async def trigger_test_notification() -> dict[str, str]:
            try:
                self.app_instance.send_test_notification()
                return {"message": "Test notification triggered"}
            except Exception:
                logger.exception("Error triggering test notification")
                raise HTTPException(
                    status_code=500, detail="Internal server error"
                ) from None

    def get_app(self) -> FastAPI:
        """Return the FastAPI application instance."""
        return self.app
