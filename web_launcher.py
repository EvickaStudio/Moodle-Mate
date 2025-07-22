#!/usr/bin/env python3
"""
Moodle-Mate Web Interface Launcher

This script launches the web interface for Moodle-Mate, providing a modern
browser-based dashboard for monitoring and configuring the notification system.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.infrastructure.logging.setup import setup_logging
from src.ui.web.app import MoodleMateWebApp


def main() -> None:
    """Main entry point for the web interface."""
    parser = argparse.ArgumentParser(
        description="Moodle-Mate Web Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Start web interface on default port (5000)
  %(prog)s --port 8080              # Start on custom port
  %(prog)s --host 0.0.0.0 --port 80 # Start on all interfaces, port 80
  %(prog)s --debug                  # Start in debug mode (development)
        """
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host address to bind to (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port", 
        type=int,
        default=5000,
        help="Port number to listen on (default: 5000)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (auto-reload, detailed errors)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--config",
        default="config.ini",
        help="Path to configuration file (default: config.ini)"
    )

    args = parser.parse_args()

    # Set up logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    # Check if config file exists
    config_path = Path(args.config)
    if not config_path.exists():
        logger.warning(f"Configuration file not found: {config_path}")
        logger.info("The web interface will start but some features may not work correctly.")
        logger.info("Please configure Moodle-Mate first or create a configuration file.")

    # Create and start the web application
    try:
        logger.info("Starting Moodle-Mate Web Interface...")
        logger.info(f"Configuration file: {config_path.absolute()}")
        
        # Set environment variable for config path if needed
        os.environ.setdefault("MOODLE_MATE_CONFIG", str(config_path.absolute()))
        
        app = MoodleMateWebApp(debug=args.debug)
        
        logger.info(f"Web interface will be available at: http://{args.host}:{args.port}")
        logger.info("Press Ctrl+C to stop the server")
        
        if args.debug:
            logger.warning("Debug mode is enabled - do not use in production!")
        
        # Start the web server
        app.run(host=args.host, port=args.port)
        
    except KeyboardInterrupt:
        logger.info("Shutting down web interface...")
    except Exception as exc:
        logger.error(f"Failed to start web interface: {exc}")
        if args.debug:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main() 