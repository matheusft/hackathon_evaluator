"""
Evaluation Engine Module
========================

Handles evaluation of participant embedding submissions.
"""

import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.metrics.pairwise import cosine_similarity


class EvaluationEngine:
    """Engine for evaluating participant embedding submissions."""

    def __init__(self, config: Optional[Any] = None):
        """
        Initialize evaluation engine.
        
        Args:
            config: EvaluationConfig object with criteria weights
        """
        if config and hasattr(config, "criteria_weights"):
            self.evaluation_criteria = config.criteria_weights
            self.scoring_config = config.scoring
        else:
            self.evaluation_criteria = {
                "accuracy": 0.4,
                "performance": 0.3,
                "completeness": 0.3,
            }
            self.scoring_config = {
                "base_score_range": {"min": 0.6, "max": 0.95},
                "completeness_bonus_max": 0.1,
                "performance_time_threshold": 10.0,
                "performance_memory_threshold": 1000.0,
            }

    def evaluate_submission(
        self,
        participant_name: str,
        submission_tag: str,
        results: Dict[str, Any],
        test_data_id: str,
    ) -> Dict[str, Any]:
        """
        Evaluate a participant's embedding submission.

        Args:
            participant_name: Name of the participant
            submission_tag: Tag for this submission
            results: Results submitted by participant
            test_data_id: ID of the test data used

        Returns:
            Evaluation result with score and details
        """
        try:
            validation_result = self._validate_submission_format(results=results)
            if not validation_result["valid"]:
                return {
                    "valid": False,
                    "error": validation_result["error"],
                    "score": 0.0,
                }

            accuracy_score = self._calculate_accuracy_score(results=results)
            performance_score = self._calculate_performance_score(
                results=results
            )
            completeness_score = self._calculate_completeness_score(
                results=results
            )

            final_score = (
                accuracy_score * self.evaluation_criteria["accuracy"]
                + performance_score * self.evaluation_criteria["performance"]
                + completeness_score * self.evaluation_criteria["completeness"]
            )

            return {
                "valid": True,
                "score": round(final_score, 3),
                "details": {
                    "accuracy_score": round(accuracy_score, 3),
                    "performance_score": round(performance_score, 3),
                    "completeness_score": round(completeness_score, 3),
                    "weighted_scores": {
                        "accuracy": round(
                            accuracy_score * self.evaluation_criteria["accuracy"],
                            3,
                        ),
                        "performance": round(
                            performance_score
                            * self.evaluation_criteria["performance"],
                            3,
                        ),
                        "completeness": round(
                            completeness_score
                            * self.evaluation_criteria["completeness"],
                            3,
                        ),
                    },
                    "criteria_weights": self.evaluation_criteria,
                },
            }

        except Exception as e:
            return {
                "valid": False,
                "error": f"Evaluation error: {str(e)}",
                "score": 0.0,
            }

    def _validate_submission_format(
        self, results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate the format of submission results."""
        required_fields = ["processed_data", "metadata"]

        for field in required_fields:
            if field not in results:
                return {
                    "valid": False,
                    "error": f"Missing required field: {field}",
                }

        if not isinstance(results["processed_data"], dict):
            return {
                "valid": False,
                "error": "processed_data must be a dictionary",
            }

        metadata = results.get("metadata", {})
        if not isinstance(metadata, dict):
            return {"valid": False, "error": "metadata must be a dictionary"}

        return {"valid": True}

    def _calculate_accuracy_score(self, results: Dict[str, Any]) -> float:
        """
        Calculate accuracy score based on embedding quality.

        Args:
            results: Submission results

        Returns:
            Accuracy score (0.0 to 1.0)
        """
        processed_data = results.get("processed_data", {})

        if not processed_data:
            return 0.0

        test_scores = []

        for test_id, test_result in processed_data.items():
            if "embeddings" not in test_result:
                continue

            embeddings = test_result.get("embeddings", [])
            if len(embeddings) < 2:
                continue

            try:
                embeddings_array = np.array(embeddings)
                
                if embeddings_array.ndim != 2:
                    continue

                score = self._evaluate_test_case_embeddings(
                    test_id=test_id, embeddings=embeddings_array
                )
                test_scores.append(score)

            except Exception:
                continue

        if not test_scores:
            return 0.0

        return np.mean(test_scores)

    def _evaluate_test_case_embeddings(
        self, test_id: str, embeddings: np.ndarray
    ) -> float:
        """
        Evaluate embeddings for a specific test case.

        Args:
            test_id: Test case identifier
            embeddings: Array of embeddings

        Returns:
            Score for this test case
        """
        if embeddings.shape[0] < 2:
            return 0.0

        similarities = cosine_similarity(embeddings)

        if "identical" in test_id:
            identical_sim = similarities[0, 1]
            return min(identical_sim, 1.0)

        elif "single_feature_diff" in test_id:
            feature_diff_sim = similarities[0, 1]
            return min(feature_diff_sim * 0.9, 1.0)

        elif "high_vs_low_spec" in test_id:
            spec_diff_sim = similarities[0, 1]
            return min((1.0 - spec_diff_sim) * 1.5, 1.0)

        elif "price_similarity" in test_id and embeddings.shape[0] >= 3:
            sim_to_similar = similarities[0, 1]
            sim_to_distant = similarities[0, 2]
            
            if sim_to_similar > sim_to_distant:
                return min((sim_to_similar - sim_to_distant) * 2.0, 1.0)
            else:
                return 0.3

        elif "same_vehicle_diff_trim" in test_id and embeddings.shape[0] >= 3:
            avg_similarity = np.mean(
                [similarities[i, j] for i in range(len(embeddings)) 
                 for j in range(i + 1, len(embeddings))]
            )
            return min(avg_similarity * 1.2, 1.0)

        else:
            avg_similarity = np.mean(similarities[np.triu_indices_from(similarities, k=1)])
            return min(avg_similarity, 1.0)

    def _calculate_performance_score(self, results: Dict[str, Any]) -> float:
        """Calculate performance score based on efficiency metrics."""
        metadata = results.get("metadata", {})

        processing_time = metadata.get("processing_time_seconds")
        memory_usage = metadata.get("memory_usage_mb")

        if processing_time is None:
            return 0.5

        time_threshold = self.scoring_config["performance_time_threshold"]
        time_score = max(
            0.0, min(1.0, (time_threshold - processing_time) / time_threshold)
        )

        if memory_usage is not None:
            memory_threshold = self.scoring_config["performance_memory_threshold"]
            memory_score = max(
                0.0,
                min(1.0, (memory_threshold - memory_usage) / memory_threshold),
            )
            return (time_score + memory_score) / 2.0

        return time_score

    def _calculate_completeness_score(self, results: Dict[str, Any]) -> float:
        """Calculate completeness score based on result coverage."""
        processed_data = results.get("processed_data", {})
        metadata = results.get("metadata", {})

        score = 0.0

        if processed_data:
            score += 0.5

        if metadata:
            score += 0.2

        if metadata.get("quality_checks_passed"):
            score += 0.2

        if metadata.get("validation_status") == "passed":
            score += 0.1

        return min(score, 1.0)