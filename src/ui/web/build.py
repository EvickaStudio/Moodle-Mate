#!/usr/bin/env python3
"""
Build script for Moodle-Mate Web Interface

This script sets up the web interface by:
1. Installing npm dependencies
2. Compiling TailwindCSS
3. Setting up static assets
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list, cwd: Path = None) -> bool:
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✓ {' '.join(cmd)}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {' '.join(cmd)}")
        print(f"Error: {e.stderr}")
        return False


def check_node_npm():
    """Check if Node.js and npm are installed."""
    print("Checking for Node.js and npm...")
    
    if not run_command(["node", "--version"]):
        print("Error: Node.js is not installed. Please install Node.js from https://nodejs.org/")
        return False
    
    if not run_command(["npm", "--version"]):
        print("Error: npm is not installed. Please install npm.")
        return False
    
    return True


def setup_web_interface():
    """Set up the web interface."""
    web_dir = Path(__file__).parent
    print(f"Setting up web interface in: {web_dir}")
    
    # Check Node.js/npm
    if not check_node_npm():
        return False
    
    # Install npm dependencies
    print("\nInstalling npm dependencies...")
    if not run_command(["npm", "install"], cwd=web_dir):
        return False
    
    # Build CSS
    print("\nBuilding CSS...")
    if not run_command(["npm", "run", "build-css-prod"], cwd=web_dir):
        print("CSS compilation failed, trying fallback...")
        # Fallback: copy existing application.css
        assets_css = web_dir / "static" / "assets" / "tailwind" / "application.css"
        output_css = web_dir / "static" / "css" / "output.css"
        
        if assets_css.exists():
            import shutil
            shutil.copy2(assets_css, output_css)
            print("✓ Copied existing application.css as fallback")
        else:
            print("✗ No fallback CSS available")
            return False
    
    print("\n🎉 Web interface setup completed successfully!")
    print(f"\nTo start the web interface:")
    print(f"cd {web_dir.parent.parent.parent}")
    print(f"python web_launcher.py")
    
    return True


if __name__ == "__main__":
    success = setup_web_interface()
    sys.exit(0 if success else 1) 