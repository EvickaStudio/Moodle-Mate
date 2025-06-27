import argparse
import logging
import sys

from src.app import MoodleMateApp
from src.core.config.generator import ConfigGenerator
from src.infrastructure.logging.setup import setup_logging
from src.ui.cli.screen import animate_logo, logo_lines


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

    app = MoodleMateApp()
    if args.test_notification:
        app.send_test_notification()
    else:
        app.run()


if __name__ == "__main__":
    main()
