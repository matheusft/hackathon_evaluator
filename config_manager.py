"""
Configuration Manager Module
============================

Handles loading and managing configuration from YAML files.
"""

import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ServerConfig:
    """Server configuration settings."""

    host: str = "0.0.0.0"
    port: int = 5001
    debug: bool = True
    secret_key: str = "dev-secret-key"


@dataclass
class EvaluationConfig:
    """Evaluation configuration settings."""

    criteria_weights: Dict[str, float] = None
    scoring: Dict[str, Any] = None

    def __post_init__(self):
        if self.criteria_weights is None:
            self.criteria_weights = {
                "accuracy": 0.4,
                "performance": 0.3,
                "completeness": 0.3,
            }
        if self.scoring is None:
            self.scoring = {
                "base_score_range": {"min": 0.6, "max": 0.95},
                "completeness_bonus_max": 0.1,
                "performance_time_threshold": 10.0,
                "performance_memory_threshold": 1000.0,
            }


@dataclass
class LeaderboardConfig:
    """Leaderboard configuration settings."""

    csv_path: str = "data/leaderboard.csv"
    max_displayed_participants: int = 100
    auto_refresh_seconds: int = 30


@dataclass
class AppConfig:
    """Main application configuration."""

    server: ServerConfig
    evaluation: EvaluationConfig
    leaderboard: LeaderboardConfig

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "AppConfig":
        """Create AppConfig from dictionary."""
        server_config = ServerConfig(**config_dict.get("server", {}))
        evaluation_config = EvaluationConfig(**config_dict.get("evaluation", {}))
        leaderboard_config = LeaderboardConfig(**config_dict.get("leaderboard", {}))

        return cls(
            server=server_config,
            evaluation=evaluation_config,
            leaderboard=leaderboard_config,
        )


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file. If None, uses default location.

    Returns:
        Loaded configuration object
    """
    if config_path is None:
        # Try multiple possible locations for config file
        possible_paths = [
            Path(__file__).parent.parent / "config" / "config.yaml",
            Path("../config/config.yaml"),
            Path("config/config.yaml"),
            Path(__file__).parent / "../config/config.yaml",
        ]
        config_path = None
        for path in possible_paths:
            if path.exists():
                config_path = path
                break

        if config_path is None:
            print("Config file not found in any expected location, using defaults")
            return AppConfig.from_dict({})

    config_path = Path(config_path)

    if not config_path.exists():
        print(f"Config file not found at {config_path}, using defaults")
        return AppConfig.from_dict({})

    try:
        with open(config_path, "r") as f:
            config_dict = yaml.safe_load(f)

        # Handle environment-specific overrides
        environment = os.environ.get("ENVIRONMENT", "development")
        if environment == "production" and "production" in config_dict:
            # Merge production overrides
            production_overrides = config_dict["production"]
            _deep_merge(config_dict, production_overrides)

        # Apply environment variable overrides
        _apply_env_overrides(config_dict)

        return AppConfig.from_dict(config_dict)

    except Exception as e:
        print(f"Error loading config from {config_path}: {e}")
        print("Using default configuration")
        return AppConfig.from_dict({})


def _deep_merge(base_dict: Dict[str, Any], override_dict: Dict[str, Any]) -> None:
    """
    Deep merge override_dict into base_dict.

    Args:
        base_dict: Base dictionary to merge into
        override_dict: Dictionary with override values
    """
    for key, value in override_dict.items():
        if (
            key in base_dict
            and isinstance(base_dict[key], dict)
            and isinstance(value, dict)
        ):
            _deep_merge(base_dict[key], value)
        else:
            base_dict[key] = value


def _apply_env_overrides(config_dict: Dict[str, Any]) -> None:
    """
    Apply environment variable overrides to config.

    Args:
        config_dict: Configuration dictionary to modify
    """
    # Common environment variables
    env_mappings = {
        "SECRET_KEY": ["server", "secret_key"],
        "PORT": ["server", "port"],
        "DEBUG": ["server", "debug"],
        "LEADERBOARD_CSV_PATH": ["leaderboard", "csv_path"],
    }

    for env_var, config_path in env_mappings.items():
        env_value = os.environ.get(env_var)
        if env_value is not None:
            # Navigate to the nested config location
            current = config_dict
            for key in config_path[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]

            # Convert value to appropriate type
            final_key = config_path[-1]
            if env_var == "PORT":
                current[final_key] = int(env_value)
            elif env_var == "DEBUG":
                current[final_key] = env_value.lower() == "true"
            else:
                current[final_key] = env_value
