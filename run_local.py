#!/usr/bin/env python3
"""
Local Development Runner
========================

Run the Flask evaluator service locally for development and testing.
"""

import os
import sys
from pathlib import Path

# Load environment variables BEFORE importing app
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if key == "db_External_Database_URL":
                    os.environ["DATABASE_URL"] = value
                    print(f"✅ Loaded DATABASE_URL from .env")

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from app import create_app
from config.config_manager import load_config


def main():
    """Run the application locally."""
    # Check if DATABASE_URL is set
    if "DATABASE_URL" not in os.environ:
        print("\n⚠️  DATABASE_URL not set!")
        print("Create a .env file with: db_External_Database_URL=postgresql://...")
        print("Or get it from: https://dashboard.render.com/d/dpg-d39ta995pdvs73bnrlj0-a")
        return

    # Load configuration
    app_config = load_config()

    # Create Flask app
    app = create_app()

    # Run development server
    port = app_config.server.port
    print("🚀 Starting Hackathon Evaluator Service...")
    print(f"📊 Leaderboard available at: http://localhost:{port}")
    print("🔗 API endpoints:")
    print("   GET  /api/test-data?participant_name=YOUR_NAME")
    print("   POST /api/submit-results")
    print("   GET  /api/leaderboard")
    print("   GET  /api/health")
    print("\n✨ Press Ctrl+C to stop the server")

    try:
        app.run(
            host=app_config.server.host,
            port=port,
            debug=app_config.server.debug,
            use_reloader=True,
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")


if __name__ == "__main__":
    main()
