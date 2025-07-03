import argparse
import logging
import sys
import threading

from src.app import MoodleMateApp
from src.core.config.generator import ConfigGenerator
from src.infrastructure.logging.setup import setup_logging
from src.ui.cli.screen import animate_logo, logo_lines
from src.ui.web.app import WebUI
from src.core.service_locator import ServiceLocator


def main() -> None:
    """Main entry point of the application."""
    parser = argparse.ArgumentParser(
        description="Moodle Mate - Your Smart Moodle Notification Assistant"
    )
    parser.add_argument(
        "--gen-config", action="store_true", help="Generate a new configuration file"
    )
    parser.add_argument("--config", default="config.ini", help="Path to config file")
    parser.add_argument(
        "--test-notification",
        action="store_true",
        help="Send a test notification to all configured providers",
    )
    parser.add_argument(
        "--web-ui", action="store_true", help="Enable the web UI"
    )
    args = parser.parse_args()

    setup_logging()

    if args.gen_config:
        if ConfigGenerator().generate_config():
            logging.info("Configuration file generated successfully!")
            sys.exit(0)
        else:
            logging.error("Failed to generate configuration file.")
            sys.exit(1)

    animate_logo(logo_lines)
    logging.info("Starting Moodle Mate...")

    reload_event = threading.Event()
    app = MoodleMateApp(reload_event)
    ServiceLocator.register("moodle_mate_app", app)

    if args.web_ui:
        web_ui = WebUI()
        web_ui.run_in_thread(reload_event)

    if args.test_notification:
        app.send_test_notification()
    else:
        app.run()


if __name__ == "__main__":
    main()
