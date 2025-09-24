"""
WSGI Entry Point for Production Deployment
"""

import os
import sys

# Debug: Print current directory and sys.path
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")
print(f"Files in current directory: {os.listdir('.')}")

# Ensure current directory is in Python path
if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

# Simple direct import
from app import create_app

# Production configuration
config_override = {
    "SECRET_KEY": os.environ.get("SECRET_KEY", "fallback-secret-key"),
    "DEBUG": False,
}

# Create application instance
app = create_app(config_override=config_override)
