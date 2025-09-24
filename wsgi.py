"""
WSGI Entry Point for Production Deployment
"""

import os
import sys

# Ensure current directory is in Python path
if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

# Import the create_app function
from app import create_app

# Production configuration
config_override = {
    "SECRET_KEY": os.environ.get("SECRET_KEY", "fallback-secret-key"),
    "DEBUG": False,
}

# Validate critical environment variables
required_env_vars = ["DATABASE_URL", "SECRET_KEY"]
missing_vars = [var for var in required_env_vars if not os.environ.get(var)]

if missing_vars:
    raise ValueError(f"Missing required environment variables: {missing_vars}")

# Create application instance
app = create_app(config_override=config_override)
