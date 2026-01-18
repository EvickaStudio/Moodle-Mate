import logging
import secrets
from pathlib import Path
from typing import Any

from fastapi import Body, Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import APIKeyCookie
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from moodlemate.config import Settings
from moodlemate.core.state_manager import StateManager
from moodlemate.infrastructure.http.request_manager import request_manager

logger = logging.getLogger(__name__)

COOKIE_NAME = "moodlemate_auth"
LOGIN_BODY = Body(...)
CONFIG_BODY = Body(...)


class WebUI:
    def __init__(
        self, settings: Settings, state_manager: StateManager, app_instance: Any
    ):
        self.settings = settings
        self.state_manager = state_manager
        self.app_instance = app_instance

        self.app = FastAPI(title="Moodle Mate WebUI")
        base_dir = Path(__file__).resolve().parent
        self.app.mount(
            "/static",
            StaticFiles(directory=str(base_dir / "static")),
            name="static",
        )
        self.templates = Jinja2Templates(directory=str(base_dir / "templates"))

        # Simple cookie auth dependency
        self.cookie_scheme = APIKeyCookie(name=COOKIE_NAME, auto_error=False)

        self._setup_routes()

    def _check_auth(self, request: Request) -> bool:
        """
        Check if the request is authenticated.
        Returns True if auth is valid or not enabled.
        """
        # If no secret set, auth is disabled (open access)
        if not self.settings.web.auth_secret:
            return True

        cookie_value = request.cookies.get(COOKIE_NAME)
        if cookie_value is None:
            return False
        # Simple check: cookie value must match the secret
        # In production, you'd hash/salt this, but requirement is "hardcoded pass"
        return secrets.compare_digest(
            str(cookie_value), str(self.settings.web.auth_secret)
        )

    async def _auth_dependency(self, request: Request):
        """Dependency to protect API routes."""
        if not self._check_auth(request):
            raise HTTPException(status_code=401, detail="Unauthorized")

    def _setup_routes(self):
        @self.app.get("/login", response_class=HTMLResponse)
        async def login_page(request: Request):
            if not self.settings.web.auth_secret:
                return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
            return self.templates.TemplateResponse("login.html", {"request": request})

        @self.app.post("/api/login")
        async def login(
            request: Request, response: Response, payload: Any = LOGIN_BODY
        ):
            if not self.settings.web.auth_secret:
                return {"message": "Auth not enabled"}

            password = None
            if isinstance(payload, dict):
                password = payload.get("password")
            elif isinstance(payload, str):
                password = payload

            if password is None:
                raise HTTPException(status_code=400, detail="Password required")

            if secrets.compare_digest(
                str(password), str(self.settings.web.auth_secret)
            ):
                # Set cookie
                response.set_cookie(
                    key=COOKIE_NAME,
                    value=password,
                    httponly=True,
                    max_age=86400 * 30,  # 30 days
                    samesite="lax",
                    secure=request.url.scheme == "https",
                )
                return {"message": "Logged in"}

            raise HTTPException(status_code=401, detail="Invalid password")

        @self.app.post("/api/logout")
        async def logout(response: Response):
            response.delete_cookie(COOKIE_NAME)
            return {"message": "Logged out"}

        @self.app.get("/", response_class=HTMLResponse)
        async def read_root(request: Request):
            if not self._check_auth(request):
                return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

            return self.templates.TemplateResponse(
                "index.html", {"request": request, "version": "2.2.0"}
            )

        @self.app.get("/api/status", dependencies=[Depends(self._auth_dependency)])
        async def get_status():
            return {
                "running": True,
                "last_notification_id": self.state_manager.last_notification_id,
            }

        @self.app.get("/api/history", dependencies=[Depends(self._auth_dependency)])
        async def get_history():
            return self.state_manager.get_history()

        @self.app.get("/api/config", dependencies=[Depends(self._auth_dependency)])
        async def get_config():
            config_dict = self.settings.model_dump()

            # Redaction
            if "moodle" in config_dict and config_dict["moodle"]["password"]:
                config_dict["moodle"]["password"] = "********"
            if "ai" in config_dict and config_dict["ai"]["api_key"]:
                config_dict["ai"]["api_key"] = "********"
            if "web" in config_dict:
                # Don't show the auth secret in config
                config_dict["web"]["auth_secret"] = "********"

            return config_dict

        @self.app.post("/api/config", dependencies=[Depends(self._auth_dependency)])
        async def update_config(new_config: dict[str, Any] = CONFIG_BODY):
            try:

                def merge_dict(target: dict[str, Any], updates: dict[str, Any]) -> None:
                    for key, value in updates.items():
                        if key == "auth_secret":
                            continue
                        if isinstance(value, dict) and isinstance(
                            target.get(key), dict
                        ):
                            merge_dict(target[key], value)
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

            except Exception as e:
                logger.error(f"Failed to update config: {e}")
                raise HTTPException(status_code=500, detail=str(e)) from e

        @self.app.post(
            "/api/test-notification", dependencies=[Depends(self._auth_dependency)]
        )
        async def trigger_test_notification():
            try:
                self.app_instance.send_test_notification()
                return {"message": "Test notification triggered"}
            except Exception as e:
                logger.error(f"Error triggering test notification: {e}")
                raise HTTPException(status_code=500, detail=str(e)) from e

    def get_app(self) -> FastAPI:
        return self.app
