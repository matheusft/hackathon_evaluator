"""
WSGI Entry Point
===============

Entry point for production deployment (Render, Heroku, etc.)
"""

import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import from src package
from src.app import create_app

# Configuration for production
config_override = {
    "SECRET_KEY": os.environ.get("SECRET_KEY", "fallback-secret-key"),
    "LEADERBOARD_CSV_PATH": os.environ.get("LEADERBOARD_CSV_PATH", "data/leaderboard.csv"),
    "DEBUG": False,
}

# Create application instance
app = create_app(config_override=config_override)

if __name__ == "__main__":
    # For development only
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)