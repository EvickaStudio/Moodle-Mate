import logging
import threading
import time
from datetime import timedelta
import uvicorn
from fastapi import Depends, FastAPI, Form, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.core.service_locator import ServiceLocator
from src.core.config.loader import Config
from src.core.notification.processor import NotificationProcessor

logger = logging.getLogger(__name__)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
limiter = Limiter(key_func=get_remote_address)

class WebUI:
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.app = FastAPI()
        self.host = host
        self.port = port
        self.templates = Jinja2Templates(directory="src/ui/web/templates")
        self.app.mount("/static", StaticFiles(directory="src/ui/web/static"), name="static")
        self.app.state.limiter = limiter
        self.app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        self._setup_routes()

    def _setup_routes(self):
        @self.app.get("/login", response_class=HTMLResponse)
        async def login_page(request: Request):
            return self.templates.TemplateResponse("login.html", {"request": request})

        @self.app.post("/login")
        @limiter.limit("5/minute")
        async def login(request: Request, password: str = Form(...)):
            config = ServiceLocator.get("config", Config)

            # Handle both hashed (bcrypt) and plaintext stored passwords
            try:
                password_valid = pwd_context.verify(password, config.webui.password)
            except UnknownHashError:
                # Stored password is not a recognised hash – fallback to plaintext comparison
                password_valid = password == config.webui.password

            if not password_valid:
                return RedirectResponse("/login?error=1", status_code=status.HTTP_302_FOUND)
            response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
            response.set_cookie(key="session", value="supersecret", httponly=True)
            return response

        @self.app.get("/logout")
        async def logout(request: Request):
            response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
            response.delete_cookie("session")
            return response

        @self.app.get("/", response_class=HTMLResponse)
        async def read_root(request: Request):
            if not request.cookies.get("session"):
                return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
            config = ServiceLocator.get("config", Config)
            return self.templates.TemplateResponse("index.html", {"request": request, "config": config.config})

        @self.app.post("/save-config")
        async def save_config(request: Request, form_data: Request):
            if not request.cookies.get("session"):
                return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
            form = await form_data.form()
            config = ServiceLocator.get("config", Config)
            for section, settings in config.config.items():
                for key in settings:
                    new_value = form.get(f"{section}.{key}")
                    if new_value is not None:
                        config.config.set(section, key, new_value)
            
            with open('config.ini', 'w') as configfile:
                config.config.write(configfile)

            logger.info("Configuration saved. Triggering reload...")
            if hasattr(self, 'reload_event'):
                self.reload_event.set()

            return RedirectResponse(url="/?message=saved", status_code=status.HTTP_302_FOUND)

        @self.app.get("/api/logs")
        async def get_logs(request: Request):
            if not request.cookies.get("session"):
                return Response(status_code=401)
            try:
                with open("logs/moodlemate.log", "r") as f:
                    lines = f.readlines()
                    return HTMLResponse("".join(lines[-50:]))
            except FileNotFoundError:
                return HTMLResponse("Log file not found.")

        @self.app.get("/api/stats")
        async def get_stats(request: Request):
            if not request.cookies.get("session"):
                return Response(status_code=401)
            app = ServiceLocator.get("moodle_mate_app", "MoodleMateApp")
            uptime = time.time() - app.start_time
            return {
                "uptime": str(timedelta(seconds=uptime)),
                "notifications_processed": app.notifications_processed,
                "errors": app.errors,
            }

        @self.app.get("/api/notifications")
        async def get_notifications(request: Request):
            if not request.cookies.get("session"):
                return Response(status_code=401)
            processor = ServiceLocator.get("notification_processor", NotificationProcessor)
            return list(processor.notification_history)

    def run_in_thread(self, reload_event: threading.Event):
        self.reload_event = reload_event
        config = uvicorn.Config(self.app, host=self.host, port=self.port, log_level="info")
        server = uvicorn.Server(config)
        thread = threading.Thread(target=server.run)
        thread.daemon = True
        thread.start()
        logger.info(f"Web UI running on http://{self.host}:{self.port}")