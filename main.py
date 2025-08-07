import argparse
import logging
import sys

from src.app import MoodleMateApp
from src.core.config.generator import ConfigGenerator
from src.infrastructure.logging.setup import setup_logging
from src.ui.cli.screen import animate_logo, clear_screen, loading_animation


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
        "--no-anim",
        action="store_true",
        help="Disable startup animation (useful for logs/CI)",
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

    # Improved startup: clear, quick spinner, then smooth centered logo
    if args.no_anim:
        animate_logo(animate=False)
    else:
        clear_screen()
        # Show spinner a bit longer so it's noticeable
        loading_animation(1.0)
        animate_logo(animate=True)
    logging.info("Starting Moodle Mate...")

    app = MoodleMateApp()
    if args.test_notification:
        app.send_test_notification()
    else:
        app.run()


if __name__ == "__main__":
    main()
