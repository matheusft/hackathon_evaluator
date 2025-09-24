#!/usr/bin/env python3
"""
Local Development Runner
========================

Run the Flask evaluator service locally for development and testing.
"""


import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from app import create_app
from config.config_manager import load_config


def main():
    """Run the application locally."""
    # Load configuration
    app_config = load_config()

    # Override for local development if needed
    config_override = {
        "LEADERBOARD_CSV_PATH": str(Path(__file__).parent / "data" / "leaderboard.csv"),
    }

    # Create Flask app
    app = create_app(config_override=config_override)

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
