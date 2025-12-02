import logging
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Body, Depends, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import APIKeyCookie

from src.config import Settings
from src.core.state_manager import StateManager

logger = logging.getLogger(__name__)

COOKIE_NAME = "moodlemate_auth"


class WebUI:
    def __init__(
        self, settings: Settings, state_manager: StateManager, app_instance: Any
    ):
        self.settings = settings
        self.state_manager = state_manager
        self.app_instance = app_instance

        self.app = FastAPI(title="Moodle Mate WebUI")
        self.app.mount(
            "/static", StaticFiles(directory="src/web/static"), name="static"
        )
        self.templates = Jinja2Templates(directory="src/web/templates")

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
        # Simple check: cookie value must match the secret
        # In production, you'd hash/salt this, but requirement is "hardcoded pass"
        return cookie_value == self.settings.web.auth_secret

    async def _auth_dependency(self, request: Request):
        """Dependency to protect API routes."""
        if not self._check_auth(request):
            raise HTTPException(status_code=401, detail="Unauthorized")

    def _setup_routes(self):
        @self.app.get("/login", response_class=HTMLResponse)
        async def login_page(request: Request):
            return self.templates.TemplateResponse("login.html", {"request": request})

        @self.app.post("/api/login")
        async def login(response: Response, password: str = Body(..., embed=True)):
            if not self.settings.web.auth_secret:
                return {"message": "Auth not enabled"}

            if password == self.settings.web.auth_secret:
                # Set cookie
                response.set_cookie(
                    key=COOKIE_NAME,
                    value=password,
                    httponly=True,
                    max_age=86400 * 30,  # 30 days
                    samesite="lax",
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
        async def update_config(new_config: Dict[str, Any] = Body(...)):
            try:

                def update_recursive(original_model, new_values):
                    for key, value in new_values.items():
                        if not hasattr(original_model, key):
                            continue

                        # Protected fields that cannot be changed via web
                        if key == "auth_secret":
                            continue

                        attr = getattr(original_model, key)
                        if hasattr(attr, "model_dump") and isinstance(value, dict):
                            update_recursive(attr, value)
                        else:
                            if value == "********":
                                continue
                            setattr(original_model, key, value)

                update_recursive(self.settings, new_config)

                logger.info("Configuration updated via WebUI")
                return {"message": "Configuration updated successfully."}

            except Exception as e:
                logger.error(f"Failed to update config: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post(
            "/api/test-notification", dependencies=[Depends(self._auth_dependency)]
        )
        async def trigger_test_notification():
            try:
                self.app_instance.send_test_notification()
                return {"message": "Test notification triggered"}
            except Exception as e:
                logger.error(f"Error triggering test notification: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    def get_app(self) -> FastAPI:
        return self.app
