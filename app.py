"""
Flask Hackathon Evaluator Service
=================================

Central evaluator service that:
1. Sends test data to participants
2. Receives results from participants
3. Evaluates the results
4. Updates leaderboard
5. Displays frontend with leaderboard
"""

from flask import Flask, request, jsonify, render_template
from typing import Dict, Any, Optional
import os
import sys
from datetime import datetime

# Ensure current directory is in Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Also add the working directory
working_dir = os.getcwd()
if working_dir not in sys.path:
    sys.path.insert(0, working_dir)

# Import core modules
try:
    from src.core.test_data_provider import TestDataProvider
    from src.core.leaderboard_manager import LeaderboardManager
    from src.core.evaluator import EvaluationEngine
    from src.core.submissions_manager import SubmissionsManager
    from config.config_manager import load_config
except ImportError:
    # Fallback to old location for transition compatibility
    try:
        from test_data_provider import TestDataProvider
        from leaderboard_manager import LeaderboardManager
        from evaluator import EvaluationEngine
        from submissions_manager import SubmissionsManager
        from config.config_manager import load_config
    except ImportError as e:
        raise ImportError(f"Failed to import required modules: {e}")


def create_app(config_override: Optional[Dict[str, Any]] = None) -> Flask:
    """
    Create and configure Flask application.

    Args:
        config_override: Optional configuration dictionary to override defaults

    Returns:
        Configured Flask app
    """
    app = Flask(__name__, template_folder="templates")

    # Load configuration from YAML
    app_config = load_config()

    # Set Flask config from our config system
    app.config.update(
        {
            "SECRET_KEY": app_config.server.secret_key,
            "DEBUG": app_config.server.debug,
        }
    )

    # Apply any runtime overrides
    if config_override:
        app.config.update(config_override)

    # Initialize components with config
    leaderboard_manager = LeaderboardManager()
    submissions_manager = SubmissionsManager()
    evaluation_engine = EvaluationEngine(config=app_config)
    test_data_provider = TestDataProvider(
        seed=app_config.test_data.seed,
        dataset_path=app_config.test_data.dataset_path,
    )

    @app.route("/")
    def index():
        """Display leaderboard frontend."""
        try:
            leaderboard_data = leaderboard_manager.get_leaderboard()
            return render_template("leaderboard.html", leaderboard=leaderboard_data)
        except Exception as e:
            return render_template("error.html", error=str(e)), 500

    @app.route("/api/health")
    def health_check():
        """Health check endpoint."""
        return jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service": "hackathon-evaluator",
            }
        )

    @app.route("/api/test-data", methods=["GET"])
    def get_test_data():
        """
        Provide test data to participants.

        Returns:
            JSON with test data for participants to process
        """
        try:
            participant_name = request.args.get("participant_name")
            submission_tag = request.args.get("submission_tag", "default")

            if not participant_name:
                return jsonify({"error": "participant_name parameter required"}), 400

            test_data = test_data_provider.generate_test_data(
                participant_name=participant_name,
                submission_tag=submission_tag,
            )

            return jsonify(test_data)

        except Exception as e:
            return jsonify({"error": f"Failed to generate test data: {str(e)}"}), 500

    @app.route("/api/submit-results", methods=["POST"])
    def submit_results():
        """
        Receive and evaluate results from participants.

        Expected JSON payload:
        {
            "participant_name": "team_name",
            "submission_tag": "v1.0",
            "results": {...},
            "test_data_id": "unique_test_id"
        }
        """
        try:
            data = request.get_json()

            if not data:
                return jsonify({"error": "JSON payload required"}), 400

            required_fields = [
                "participant_name",
                "submission_tag",
                "results",
                "test_data_id",
            ]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                return (
                    jsonify({"error": f"Missing required fields: {missing_fields}"}),
                    400,
                )

            # Evaluate the submitted results
            evaluation_result = evaluation_engine.evaluate_submission(
                participant_name=data["participant_name"],
                submission_tag=data["submission_tag"],
                results=data["results"],
                test_data_id=data["test_data_id"],
            )

            if not evaluation_result["valid"]:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "error": evaluation_result["error"],
                            "score": 0.0,
                        }
                    ),
                    400,
                )

            # Update leaderboard
            leaderboard_manager.update_leaderboard(
                participant_name=data["participant_name"],
                submission_tag=data["submission_tag"],
                score=evaluation_result["score"],
            )

            # Get current rank
            current_rank = leaderboard_manager.get_participant_rank(
                participant_name=data["participant_name"]
            )

            # Record submission with individual test scores (non-blocking)
            test_scores = evaluation_result.get("details", {}).get("test_scores", {})
            success = submissions_manager.record_submission(
                user_name=data["participant_name"],
                submission_tag=data["submission_tag"],
                final_score=evaluation_result["score"],
                test_scores=test_scores,
                leaderboard_rank=current_rank,
            )
            if not success:
                print(f"Warning: Could not record submission to database for {data['participant_name']}")

            return jsonify(
                {
                    "status": "success",
                    "score": evaluation_result["score"],
                    "rank": current_rank,
                    "evaluation_details": evaluation_result.get("details", {}),
                    "message": (
                        f"Submission successful! Score: "
                        f'{evaluation_result["score"]:.3f}'
                    ),
                }
            )

        except Exception as e:
            return jsonify({"error": f"Evaluation failed: {str(e)}"}), 500

    @app.route("/api/leaderboard")
    def api_leaderboard():
        """Get leaderboard data as JSON."""
        try:
            leaderboard_data = leaderboard_manager.get_leaderboard()
            return jsonify(
                {
                    "status": "success",
                    "leaderboard": leaderboard_data,
                    "total_participants": len(leaderboard_data),
                }
            )
        except Exception as e:
            return jsonify({"error": f"Failed to get leaderboard: {str(e)}"}), 500

    return app


if __name__ == "__main__":
    # Only create app if running directly (not when imported)
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config["DEBUG"])
