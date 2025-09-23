"""
WSGI Entry Point for Production Deployment
"""

import os

# Simple direct import
from app import create_app

# Production configuration
config_override = {
    "SECRET_KEY": os.environ.get("SECRET_KEY", "fallback-secret-key"),
    "LEADERBOARD_CSV_PATH": os.environ.get("LEADERBOARD_CSV_PATH", "data/leaderboard.csv"),
    "DEBUG": False,
}

# Create application instance
app = create_app(config_override=config_override)