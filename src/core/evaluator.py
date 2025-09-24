"""
Evaluation Engine Module
========================

Handles evaluation of participant embedding submissions with test-specific metrics.
"""

from typing import Any, Dict, Optional

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class EvaluationEngine:
    """Engine for evaluating participant embedding submissions."""

    def __init__(self, config: Optional[Any] = None):
        """Initialize evaluation engine.

        Args:
            config: Configuration object with test weights and thresholds
        """
        if config and hasattr(config, "test_data"):
            self.test_weights = config.test_data.test_weights
            self.thresholds = config.test_data.thresholds
        else:
            self.test_weights = {
                "price_extremes": 0.15,
                "single_option_difference": 0.15,
                "model_year_sensitivity": 0.10,
                "color_sensitivity": 0.10,
                "trim_level_similarity": 0.10,
                "vehicle_line_separation": 0.10,
                "derivative_clustering": 0.10,
                "feature_count_correlation": 0.10,
                "transitivity": 0.05,
                "cross_year_comparison": 0.05,
            }
            self.thresholds = {
                "high_similarity": 0.85,
                "low_similarity": 0.30,
                "single_option_diff_min": 0.75,
            }

    def evaluate_submission(
        self,
        participant_name: str,
        submission_tag: str,
        results: Dict[str, Any],
        test_data_id: str,
    ) -> Dict[str, Any]:
        """Evaluate a participant's embedding submission.

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

            test_scores = self._evaluate_all_tests(results=results)

            test_weight_mapping = {
                "test_1": self.test_weights.get("price_extremes", 0.15),
                "test_2": self.test_weights.get("single_option_difference", 0.15),
                "test_3": self.test_weights.get("model_year_sensitivity", 0.10),
                "test_4": self.test_weights.get("color_sensitivity", 0.10),
                "test_5": self.test_weights.get("trim_level_similarity", 0.10),
                "test_6": self.test_weights.get("vehicle_line_separation", 0.10),
                "test_7": self.test_weights.get("derivative_clustering", 0.10),
                "test_8": self.test_weights.get("feature_count_correlation", 0.10),
                "test_9": self.test_weights.get("transitivity", 0.05),
                "test_10": self.test_weights.get("cross_year_comparison", 0.05),
            }

            final_score = sum(
                test_scores.get(test_id, 0.0) * test_weight_mapping.get(test_id, 0.0)
                for test_id in test_weight_mapping.keys()
            )

            return {
                "valid": True,
                "score": round(final_score, 3),
                "details": {
                    "test_scores": {k: round(v, 3) for k, v in test_scores.items()},
                },
            }

        except Exception as e:
            return {
                "valid": False,
                "error": f"Evaluation error: {str(e)}",
                "score": 0.0,
            }

    def _validate_submission_format(self, results: Dict[str, Any]) -> Dict[str, Any]:
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

        return {"valid": True}

    def _evaluate_all_tests(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate all test cases and return individual scores."""
        processed_data = results.get("processed_data", {})
        test_scores = {}

        test_evaluators = {
            "test_1": self._evaluate_price_extremes,
            "test_2": self._evaluate_single_option_diff,
            "test_3": self._evaluate_model_year_sensitivity,
            "test_4": self._evaluate_color_sensitivity,
            "test_5": self._evaluate_trim_similarity,
            "test_6": self._evaluate_vehicle_line_separation,
            "test_7": self._evaluate_derivative_clustering,
            "test_8": self._evaluate_feature_correlation,
            "test_9": self._evaluate_transitivity,
            "test_10": self._evaluate_cross_year,
        }

        for test_id, evaluator_func in test_evaluators.items():
            if test_id in processed_data:
                test_result = processed_data[test_id]
                embeddings = test_result.get("embeddings", [])

                if embeddings:
                    try:
                        embeddings_array = np.array(embeddings)
                        score = evaluator_func(embeddings=embeddings_array)
                        test_scores[test_id] = score
                    except Exception:
                        test_scores[test_id] = 0.0

        return test_scores

    def _evaluate_price_extremes(self, embeddings: np.ndarray) -> float:
        """Test 1: Most expensive and least expensive should be dissimilar."""
        if embeddings.shape[0] != 2:
            return 0.0

        similarity = cosine_similarity(embeddings[0:1], embeddings[1:2])[0, 0]

        # Score = 1.0 if very dissimilar (similarity < 0.30)
        if similarity < self.thresholds["low_similarity"]:
            return 1.0
        # Score = 0.0 if very similar (similarity > 0.85)
        elif similarity > self.thresholds["high_similarity"]:
            return 0.0
        # Linear interpolation for similarities between 0.30 and 0.85
        # Higher similarity = lower score
        # Example: similarity=0.50 -> score = (0.85-0.50)/(0.85-0.30) = 0.636
        else:
            normalized = (self.thresholds["high_similarity"] - similarity) / (
                self.thresholds["high_similarity"] - self.thresholds["low_similarity"]
            )
            return max(0.0, min(1.0, normalized))

    def _evaluate_single_option_diff(self, embeddings: np.ndarray) -> float:
        """Test 2: Single option difference should be highly similar, very different should be dissimilar."""
        if embeddings.shape[0] != 3:
            return 0.0

        # Config A vs Config B (differ by 1 option) - should be highly similar
        sim_a_to_similar = cosine_similarity(embeddings[0:1], embeddings[1:2])[0, 0]
        # Config A vs Config C (differ by >5 options) - should be dissimilar
        sim_a_to_different = cosine_similarity(embeddings[0:1], embeddings[2:3])[0, 0]

        # Score for similar pair: full score if >= 0.75, scaled below
        # Example: sim=0.80 -> score=1.0, sim=0.60 -> score=0.60/0.75=0.80
        similar_score = (
            1.0
            if sim_a_to_similar >= self.thresholds["single_option_diff_min"]
            else sim_a_to_similar / self.thresholds["single_option_diff_min"]
        )

        # Score for different pair: full score if < 0.30, scaled penalty above
        # Example: sim=0.20 -> score=1.0, sim=0.50 -> score=(0.85-0.50)/(0.85-0.30)=0.636
        different_score = (
            1.0
            if sim_a_to_different < self.thresholds["low_similarity"]
            else (self.thresholds["high_similarity"] - sim_a_to_different)
            / (
                self.thresholds["high_similarity"] - self.thresholds["low_similarity"]
            )
        )

        # Ranking bonus: penalize if similar pair is not more similar than different pair
        ranking_bonus = 1.0 if sim_a_to_similar > sim_a_to_different else 0.5

        # Final score: 40% similar quality + 40% different quality + 20% correct ranking
        return similar_score * 0.4 + different_score * 0.4 + ranking_bonus * 0.2

    def _evaluate_model_year_sensitivity(self, embeddings: np.ndarray) -> float:
        """Test 3: Model year difference should have moderate impact."""
        if embeddings.shape[0] != 2:
            return 0.0

        similarity = cosine_similarity(embeddings[0:1], embeddings[1:2])[0, 0]

        # Ideal similarity range for model year difference: 0.50 to 0.75
        # Not too similar (they're different years), not too dissimilar (same vehicle/derivative)
        ideal_range = (0.50, 0.75)

        # Full score if within ideal range
        if ideal_range[0] <= similarity <= ideal_range[1]:
            return 1.0
        # Below ideal: too dissimilar, scaled score
        # Example: sim=0.30 -> score=0.30/0.50=0.60
        elif similarity < ideal_range[0]:
            return similarity / ideal_range[0]
        # Above ideal: too similar, scaled penalty
        # Example: sim=0.85 -> score=1.0-(0.85-0.75)/(1.0-0.75)=0.60
        else:
            return max(0.0, 1.0 - (similarity - ideal_range[1]) / (1.0 - ideal_range[1]))

    def _evaluate_color_sensitivity(self, embeddings: np.ndarray) -> float:
        """Test 4: Color difference should have minimal impact (high similarity expected)."""
        if embeddings.shape[0] != 2:
            return 0.0

        similarity = cosine_similarity(embeddings[0:1], embeddings[1:2])[0, 0]

        # Color-only difference should result in very high similarity (>= 0.85)
        if similarity >= self.thresholds["high_similarity"]:
            return 1.0
        # Penalty if similarity is too low (< 0.70)
        elif similarity < 0.70:
            return 0.0
        # Linear scaling between 0.70 and 0.85
        # Example: sim=0.78 -> score=(0.78-0.70)/(0.85-0.70)=0.533
        else:
            return (similarity - 0.70) / (self.thresholds["high_similarity"] - 0.70)

    def _evaluate_trim_similarity(self, embeddings: np.ndarray) -> float:
        """Test 5: Same vehicle/year, different trims should show moderate similarity."""
        if embeddings.shape[0] < 2:
            return 0.0

        # Calculate all pairwise similarities
        similarities = cosine_similarity(embeddings)
        # Average of upper triangle (excluding diagonal) = mean pairwise similarity
        avg_similarity = np.mean(similarities[np.triu_indices_from(similarities, k=1)])

        # Ideal range: 0.55 to 0.80 (moderately similar, not identical)
        ideal_range = (0.55, 0.80)

        # Full score if average similarity is within ideal range
        if ideal_range[0] <= avg_similarity <= ideal_range[1]:
            return 1.0
        # Below ideal: too dissimilar, scaled score
        # Example: avg_sim=0.40 -> score=0.40/0.55=0.727
        elif avg_similarity < ideal_range[0]:
            return avg_similarity / ideal_range[0]
        # Above ideal: too similar, scaled penalty
        # Example: avg_sim=0.90 -> score=1.0-(0.90-0.80)/(1.0-0.80)=0.50
        else:
            return max(0.0, 1.0 - (avg_similarity - ideal_range[1]) / (1.0 - ideal_range[1]))

    def _evaluate_vehicle_line_separation(self, embeddings: np.ndarray) -> float:
        """Test 6: Different vehicle lines should be clearly separated."""
        if embeddings.shape[0] < 2:
            return 0.0

        # Calculate all pairwise similarities between different vehicle lines
        similarities = cosine_similarity(embeddings)
        avg_similarity = np.mean(similarities[np.triu_indices_from(similarities, k=1)])

        # Full score if average similarity is very low (< 0.30)
        if avg_similarity < self.thresholds["low_similarity"]:
            return 1.0
        # Zero score if too similar (> 0.65)
        elif avg_similarity > 0.65:
            return 0.0
        # Linear interpolation between 0.30 and 0.65
        # Lower similarity = higher score (we want separation)
        # Example: avg_sim=0.45 -> score=(0.65-0.45)/(0.65-0.30)=0.571
        else:
            return (0.65 - avg_similarity) / (0.65 - self.thresholds["low_similarity"])

    def _evaluate_derivative_clustering(self, embeddings: np.ndarray) -> float:
        """Test 7: Same derivative should cluster together, different derivative should be separate."""
        if embeddings.shape[0] != 4:
            return 0.0

        # Calculate similarities within same derivative (first 3 embeddings)
        same_derivative_sims = []
        for i in range(3):
            for j in range(i + 1, 3):
                sim = cosine_similarity(embeddings[i : i + 1], embeddings[j : j + 1])[
                    0, 0
                ]
                same_derivative_sims.append(sim)

        # Calculate similarities to different derivative (4th embedding)
        different_derivative_sims = []
        for i in range(3):
            sim = cosine_similarity(embeddings[i : i + 1], embeddings[3:4])[0, 0]
            different_derivative_sims.append(sim)

        avg_same = np.mean(same_derivative_sims)
        avg_different = np.mean(different_derivative_sims)

        # Clustering quality: same-derivative should be more similar than different
        clustering_score = 1.0 if avg_same > avg_different else 0.5

        # Same-derivative similarity score: full score if >= 0.70
        # Example: avg_same=0.75 -> score=1.0, avg_same=0.50 -> score=0.50/0.70=0.714
        same_score = 1.0 if avg_same >= 0.70 else avg_same / 0.70

        # Different-derivative dissimilarity score: full score if < 0.50
        # Example: avg_diff=0.40 -> score=1.0, avg_diff=0.70 -> score=(0.80-0.70)/0.30=0.333
        different_score = (
            1.0 if avg_different < 0.50 else max(0.0, (0.80 - avg_different) / 0.30)
        )

        # Final score: 40% clustering + 30% same quality + 30% different quality
        return clustering_score * 0.4 + same_score * 0.3 + different_score * 0.3

    def _evaluate_feature_correlation(self, embeddings: np.ndarray) -> float:
        """Test 8: Feature count should correlate with similarity patterns."""
        if embeddings.shape[0] != 3:
            return 0.0

        # Low-feature vs mid-feature configs
        sim_low_mid = cosine_similarity(embeddings[0:1], embeddings[1:2])[0, 0]
        # Mid-feature vs high-feature configs
        sim_mid_high = cosine_similarity(embeddings[1:2], embeddings[2:3])[0, 0]
        # Low-feature vs high-feature configs
        sim_low_high = cosine_similarity(embeddings[0:1], embeddings[2:3])[0, 0]

        # Monotonic relationship: closer feature counts should be more similar
        # Good: low-mid > low-high AND mid-high > low-high
        monotonic = (
            1.0
            if (sim_low_mid > sim_low_high and sim_mid_high > sim_low_high)
            else 0.5
        )

        # Similarities should be in moderate range (not too high, not too low)
        ideal_range = (0.30, 0.65)
        avg_sim = np.mean([sim_low_mid, sim_mid_high, sim_low_high])

        # Range score: full if within 0.30-0.65, penalty based on distance from center (0.475)
        # Example: avg_sim=0.50 -> score=1.0, avg_sim=0.80 -> score=1.0-|0.80-0.475|/0.5=0.35
        range_score = (
            1.0
            if ideal_range[0] <= avg_sim <= ideal_range[1]
            else max(0.0, 1.0 - abs(avg_sim - np.mean(ideal_range)) / 0.5)
        )

        # Final score: 50% monotonic relationship + 50% appropriate range
        return monotonic * 0.5 + range_score * 0.5

    def _evaluate_transitivity(self, embeddings: np.ndarray) -> float:
        """Test 9: Transitivity - if A~B and B~C, then A should be similar to C."""
        if embeddings.shape[0] < 3:
            return 0.0

        # Calculate pairwise similarities
        sim_ab = cosine_similarity(embeddings[0:1], embeddings[1:2])[0, 0]
        sim_bc = cosine_similarity(embeddings[1:2], embeddings[2:3])[0, 0]
        sim_ac = cosine_similarity(embeddings[0:1], embeddings[2:3])[0, 0]

        # Minimum of the two "connected" similarities
        min_pairwise = min(sim_ab, sim_bc)

        # Transitivity: A-C similarity should be at least 80% of min(A-B, B-C)
        # Example: if min_pairwise=0.70, then sim_ac should be >= 0.56 for full score
        if sim_ac >= min_pairwise * 0.8:
            return 1.0
        # Partial credit if >= 60%
        # Example: if sim_ac=0.45 and min=0.70, score=0.7 (since 0.45 >= 0.70*0.6=0.42)
        elif sim_ac >= min_pairwise * 0.6:
            return 0.7
        # Scaled penalty below 60%
        # Example: if sim_ac=0.30 and min=0.70, score=0.30/(0.70*0.6)=0.714
        else:
            return max(0.0, sim_ac / (min_pairwise * 0.6))

    def _evaluate_cross_year(self, embeddings: np.ndarray) -> float:
        """Test 10: Same config pattern across years should be moderately similar."""
        if embeddings.shape[0] != 2:
            return 0.0

        similarity = cosine_similarity(embeddings[0:1], embeddings[1:2])[0, 0]

        # Ideal range: 0.60 to 0.85 (similar config but different years)
        ideal_range = (0.60, 0.85)

        # Full score if within ideal range
        if ideal_range[0] <= similarity <= ideal_range[1]:
            return 1.0
        # Below ideal: too dissimilar for same config pattern
        # Example: sim=0.40 -> score=0.40/0.60=0.667
        elif similarity < ideal_range[0]:
            return similarity / ideal_range[0]
        # Above ideal: too similar despite year difference
        # Example: sim=0.92 -> score=1.0-(0.92-0.85)/(1.0-0.85)=0.533
        else:
            return max(0.0, 1.0 - (similarity - ideal_range[1]) / (1.0 - ideal_range[1]))

    def _calculate_performance_score(self, results: Dict[str, Any]) -> float:
        """Calculate performance score based on efficiency metrics."""
        metadata = results.get("metadata", {})

        processing_time = metadata.get("processing_time_seconds")
        memory_usage = metadata.get("memory_usage_mb")

        if processing_time is None:
            return 0.5

        time_score = max(0.0, min(1.0, (10.0 - processing_time) / 10.0))

        if memory_usage is not None:
            memory_score = max(0.0, min(1.0, (1000.0 - memory_usage) / 1000.0))
            return (time_score + memory_score) / 2.0

        return time_score

    def _calculate_completeness_score(self, results: Dict[str, Any]) -> float:
        """Calculate completeness score based on result coverage."""
        processed_data = results.get("processed_data", {})
        metadata = results.get("metadata", {})

        expected_tests = 10
        actual_tests = len([k for k in processed_data.keys() if k.startswith("test_")])

        coverage_score = actual_tests / expected_tests

        metadata_score = 0.2 if metadata else 0.0

        return min(coverage_score * 0.8 + metadata_score, 1.0)