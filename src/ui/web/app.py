"""
Moodle-Mate Web Interface

A modern web frontend for the Moodle notification monitoring system.
Provides configuration management, monitoring, and notification history.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

from flask import Flask, jsonify, render_template, request, send_from_directory

from src.core.config.loader import Config
from src.core.notification.processor import NotificationProcessor
from src.core.service_locator import ServiceLocator
from src.core.services import initialize_services
from src.core.state_manager import StateManager
from src.services.moodle.api import MoodleAPI
from src.services.moodle.notification_handler import MoodleNotificationHandler


class MoodleMateWebApp:
    """
    Main web application for Moodle-Mate.

    Provides a modern web interface for configuring and monitoring
    the Moodle notification system with real-time status updates.
    """

    def __init__(self, debug: bool = False) -> None:
        """
        Initialize the web application.

        Args:
            debug: Enable Flask debug mode for development
        """
        self.app = Flask(
            __name__,
            template_folder="templates",
            static_folder="static",
            static_url_path="/static"
        )
        self.app.config["DEBUG"] = debug
        self.debug = debug
        
        # Initialize backend services
        self._initialize_services()
        self._setup_routes()
        
        # Set up logging
        if not debug:
            logging.getLogger("werkzeug").setLevel(logging.WARNING)

    def _initialize_services(self) -> None:
        """Initialize and configure backend services."""
        try:
            initialize_services()
            locator = ServiceLocator()
            
            self.config = locator.get("config", Config)
            self.notification_processor = locator.get(
                "notification_processor", NotificationProcessor
            )
            self.moodle_handler = locator.get(
                "moodle_handler", MoodleNotificationHandler
            )
            self.moodle_api = locator.get("moodle_api", MoodleAPI)
            self.state_manager = locator.get("state_manager", StateManager)
            
            logging.info("Backend services initialized successfully")
        except Exception as exc:
            logging.error(f"Failed to initialize services: {exc}")
            # Create fallback empty services for development
            self.config = None
            self.notification_processor = None
            self.moodle_handler = None
            self.moodle_api = None
            self.state_manager = None

    def _setup_routes(self) -> None:
        """Configure all Flask routes."""
        # Static file routes
        @self.app.route("/")
        def index():
            """Main dashboard page."""
            return render_template("dashboard.html")

        @self.app.route("/config")
        def config_page():
            """Configuration management page."""
            return render_template("config.html")

        @self.app.route("/notifications")
        def notifications_page():
            """Notification history and monitoring page."""
            return render_template("notifications.html")

        @self.app.route("/health")
        def health_page():
            """System health and status monitoring page."""
            return render_template("health.html")

        # Serve TailwindCSS and assets
        @self.app.route("/assets/<path:filename>")
        def assets(filename):
            """Serve CSS and other assets."""
            return send_from_directory("static/assets", filename)
            
        @self.app.route("/service-worker.js")
        def service_worker():
            """Serve the service worker."""
            return send_from_directory("static/js", "service-worker.js")
            
        @self.app.route("/favicon.ico")
        def favicon():
            """Serve the favicon."""
            return send_from_directory("static", "favicon.svg")

        # API Routes
        @self.app.route("/api/status")
        def api_status():
            """Get current system status."""
            return jsonify(self._get_system_status())

        @self.app.route("/api/config", methods=["GET", "POST"])
        def api_config():
            """Get or update configuration."""
            if request.method == "GET":
                return jsonify(self._get_config_data())
            else:
                return jsonify(self._update_config(request.json))

        @self.app.route("/api/notifications")
        def api_notifications():
            """Get recent notifications."""
            limit = request.args.get("limit", 50, type=int)
            return jsonify(self._get_recent_notifications(limit))

        @self.app.route("/api/test-notification", methods=["POST"])
        def api_test_notification():
            """Send a test notification."""
            return jsonify(self._send_test_notification())

        @self.app.route("/api/test-connection", methods=["POST"])
        def api_test_connection():
            """Test Moodle connection."""
            return jsonify(self._test_moodle_connection())

        @self.app.route("/api/providers")
        def api_providers():
            """Get available notification providers."""
            return jsonify(self._get_notification_providers())

    def _get_system_status(self) -> Dict:
        """Get current system health and status."""
        try:
            if not self.config:
                return {
                    "status": "error",
                    "message": "Services not initialized",
                    "moodle_connected": False,
                    "providers_configured": 0,
                    "last_notification": None
                }

            # Check Moodle connection
            moodle_connected = False
            try:
                if self.moodle_api:
                    info = self.moodle_api.get_site_info()
                    moodle_connected = info is not None
            except Exception:
                pass

            # Count configured providers
            providers_count = 0
            if self.notification_processor:
                providers_count = len(self.notification_processor.providers)

            # Get last notification info
            last_notification = None
            if self.state_manager:
                try:
                    with open(self.state_manager.state_file, "r") as f:
                        state = json.load(f)
                        last_id = state.get("last_notification_id")
                        if last_id:
                            last_notification = {
                                "id": last_id,
                                "timestamp": state.get("last_fetch_time")
                            }
                except (FileNotFoundError, json.JSONDecodeError):
                    pass

            return {
                "status": "healthy" if moodle_connected else "warning",
                "message": "System operational" if moodle_connected else "Moodle connection issues",
                "moodle_connected": moodle_connected,
                "providers_configured": providers_count,
                "last_notification": last_notification,
                "uptime": datetime.now().isoformat()
            }

        except Exception as exc:
            logging.error(f"Error getting system status: {exc}")
            return {
                "status": "error",
                "message": f"Error: {str(exc)}",
                "moodle_connected": False,
                "providers_configured": 0,
                "last_notification": None
            }

    def _get_config_data(self) -> Dict:
        """Get current configuration for the frontend."""
        if not self.config:
            return {"error": "Configuration not available"}

        try:
            return {
                "moodle": {
                    "url": self.config.moodle.url,
                    "username": self.config.moodle.username,
                    "initial_fetch_count": self.config.moodle.initial_fetch_count
                },
                "ai": {
                    "enabled": self.config.ai.enabled,
                    "model": self.config.ai.model,
                    "temperature": self.config.ai.temperature,
                    "max_tokens": self.config.ai.max_tokens,
                    "system_prompt": self.config.ai.system_prompt
                },
                "notification": {
                    "fetch_interval": self.config.notification.fetch_interval,
                    "max_retries": self.config.notification.max_retries
                },
                "health": {
                    "enabled": self.config.health.enabled,
                    "heartbeat_interval": self.config.health.heartbeat_interval,
                    "failure_alert_threshold": self.config.health.failure_alert_threshold,
                    "target_provider": self.config.health.target_provider
                },
                "filters": {
                    "ignore_subjects_containing": self.config.filters.ignore_subjects_containing,
                    "ignore_courses_by_id": self.config.filters.ignore_courses_by_id
                }
            }
        except Exception as exc:
            logging.error(f"Error getting config data: {exc}")
            return {"error": str(exc)}

    def _get_recent_notifications(self, limit: int) -> Dict:
        """Get recent notifications for display."""
        try:
            if not self.moodle_handler:
                return {"notifications": [], "error": "Service not available"}

            notifications = self.moodle_handler.fetch_notifications(limit)
            if notifications:
                return {
                    "notifications": [
                        {
                            "id": notif["id"],
                            "subject": notif["subject"],
                            "message": notif.get("fullmessagehtml", ""),
                            "timestamp": datetime.now().isoformat()  # Simplified
                        }
                        for notif in notifications
                    ]
                }
            return {"notifications": []}

        except Exception as exc:
            logging.error(f"Error getting notifications: {exc}")
            return {"notifications": [], "error": str(exc)}

    def _send_test_notification(self) -> Dict:
        """Send a test notification through all configured providers."""
        try:
            if not self.notification_processor:
                return {"success": False, "error": "Service not available"}

            test_data = {
                "id": 999999,
                "useridfrom": 0,
                "subject": "Moodle-Mate Web Test",
                "fullmessagehtml": "<p>This is a test notification sent from the Moodle-Mate web interface!</p>"
            }

            self.notification_processor.process(test_data)
            return {"success": True, "message": "Test notification sent successfully"}

        except Exception as exc:
            logging.error(f"Error sending test notification: {exc}")
            return {"success": False, "error": str(exc)}

    def _test_moodle_connection(self) -> Dict:
        """Test the connection to Moodle."""
        try:
            if not self.moodle_api:
                return {"success": False, "error": "Moodle API not available"}

            site_info = self.moodle_api.get_site_info()
            if site_info:
                return {
                    "success": True,
                    "site_name": site_info.get("sitename", "Unknown"),
                    "version": site_info.get("release", "Unknown")
                }
            else:
                return {"success": False, "error": "Failed to get site info"}

        except Exception as exc:
            logging.error(f"Error testing Moodle connection: {exc}")
            return {"success": False, "error": str(exc)}

    def _get_notification_providers(self) -> Dict:
        """Get information about available notification providers."""
        try:
            if not self.notification_processor:
                return {"providers": []}

            providers = []
            for provider in self.notification_processor.providers:
                providers.append({
                    "name": provider.provider_name,
                    "enabled": True  # If it's in the list, it's enabled
                })

            return {"providers": providers}

        except Exception as exc:
            logging.error(f"Error getting providers: {exc}")
            return {"providers": [], "error": str(exc)}

    def _update_config(self, config_data: Dict) -> Dict:
        """Update configuration (simplified for now)."""
        # This would need to be implemented to actually update the config file
        return {"success": False, "error": "Configuration updates not yet implemented"}

    def run(self, host: str = "127.0.0.1", port: int = 5000) -> None:
        """
        Start the web server.

        Args:
            host: Host address to bind to
            port: Port number to listen on
        """
        logging.info(f"Starting Moodle-Mate web interface on {host}:{port}")
        self.app.run(host=host, port=port, debug=self.debug)


def create_app(debug: bool = False) -> Flask:
    """
    Factory function to create Flask app instance.

    Args:
        debug: Enable debug mode

    Returns:
        Configured Flask application
    """
    web_app = MoodleMateWebApp(debug=debug)
    return web_app.app


if __name__ == "__main__":
    app = MoodleMateWebApp(debug=True)
    app.run() 