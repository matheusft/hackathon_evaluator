#!/usr/bin/env python3
"""
Test Workflow Script
===================

Demonstrates the complete participant workflow:
1. Request test data
2. Process the data (mock processing)
3. Submit results
4. Check leaderboard
"""

import requests
import json
import time
from typing import Dict, Any


def test_participant_workflow(
    base_url: str = "http://localhost:5001",
    participant_name: str = "DemoParticipant",
    submission_tag: str = "v1.0",
) -> None:
    """
    Test the complete participant workflow.

    Args:
        base_url: Base URL of the evaluator service
        participant_name: Name of the participant
        submission_tag: Submission tag
    """
    print(f"🧪 Testing workflow for {participant_name} ({submission_tag})")
    print("=" * 60)

    # Step 1: Request test data
    print("📥 Step 1: Requesting test data...")
    test_data_response = requests.get(
        f"{base_url}/api/test-data",
        params={"participant_name": participant_name, "submission_tag": submission_tag},
    )

    if test_data_response.status_code != 200:
        print(f"❌ Failed to get test data: {test_data_response.text}")
        return

    test_data = test_data_response.json()["test_data"]
    print(f"✅ Received test data with ID: {test_data['test_data_id']}")
    print(f"📋 Got {len(test_data['test_cases'])} test cases")

    # Step 2: Mock processing of test data
    print("\n⚙️  Step 2: Processing test data...")
    processed_results = process_test_data(test_data["test_cases"])
    print(f"✅ Processed {len(processed_results)} test cases")

    # Step 3: Submit results
    print("\n📤 Step 3: Submitting results...")
    submission_payload = {
        "participant_name": participant_name,
        "submission_tag": submission_tag,
        "test_data_id": test_data["test_data_id"],
        "results": {
            "processed_data": processed_results,
            "metadata": {
                "processing_time_seconds": 1.5,
                "memory_usage_mb": 85,
                "quality_checks_passed": True,
                "validation_status": "passed",
            },
        },
    }

    submit_response = requests.post(
        f"{base_url}/api/submit-results",
        json=submission_payload,
        headers={"Content-Type": "application/json"},
    )

    if submit_response.status_code != 200:
        print(f"❌ Submission failed: {submit_response.text}")
        return

    submission_result = submit_response.json()
    print(f"✅ Submission successful!")
    print(f"🎯 Score: {submission_result['score']}")
    print(f"🏆 Rank: #{submission_result['rank']}")

    # Step 4: Check leaderboard
    print("\n📊 Step 4: Checking leaderboard...")
    leaderboard_response = requests.get(f"{base_url}/api/leaderboard")

    if leaderboard_response.status_code != 200:
        print(f"❌ Failed to get leaderboard: {leaderboard_response.text}")
        return

    leaderboard_data = leaderboard_response.json()
    print(f"✅ Leaderboard has {leaderboard_data['total_participants']} participants")

    # Show top 3
    top_3 = leaderboard_data["leaderboard"][:3]
    print("\n🏆 Top 3 Participants:")
    for entry in top_3:
        medal = (
            ["🥇", "🥈", "🥉"][entry["rank"] - 1]
            if entry["rank"] <= 3
            else f"#{entry['rank']}"
        )
        print(
            f"  {medal} {entry['participant_name']} - {entry['formatted_score']} ({entry['submission_tag']})"
        )

    print(f"\n🎉 Workflow complete! Visit {base_url} to see the leaderboard.")


def process_test_data(test_cases: list) -> Dict[str, Any]:
    """
    Mock processing of test cases.

    Args:
        test_cases: List of test cases to process

    Returns:
        Dictionary with processed results
    """
    results = {}

    for test_case in test_cases:
        test_id = test_case["test_id"]
        test_type = test_case["type"]
        input_data = test_case["input_data"]

        # Mock processing based on test type
        if test_type == "simple_math":
            if input_data["operation"] == "add":
                result = sum(input_data["numbers"])
            elif input_data["operation"] == "multiply":
                result = 1
                for num in input_data["numbers"]:
                    result *= num
            elif input_data["operation"] == "subtract":
                result = input_data["numbers"][0] - input_data["numbers"][1]
            else:
                result = 0

            results[test_id] = {
                "result": result,
                "operation_performed": f"{input_data['operation']} on {input_data['numbers']}",
            }

        elif test_type == "text_processing":
            text = input_data["text"]
            task = input_data["task"]

            if task == "count_words":
                result = len(text.split())
            elif task == "reverse":
                result = text[::-1]
            elif task == "uppercase":
                result = text.upper()
            else:
                result = text

            results[test_id] = {
                "result": result,
                "original_text": text,
                "task_completed": True,
            }

        elif test_type == "data_analysis":
            dataset = input_data["dataset"]
            task = input_data["task"]

            if task == "calculate_mean":
                result = sum(dataset) / len(dataset)
            elif task == "find_max":
                result = max(dataset)
            elif task == "sum_all":
                result = sum(dataset)
            else:
                result = 0

            results[test_id] = {
                "result": result,
                "dataset_size": len(dataset),
                "calculation_method": task,
            }

    return results


if __name__ == "__main__":
    # Test multiple participants
    participants = [
        ("TeamAlpha", "v1.0"),
        ("TeamBeta", "v2.1"),
        ("TeamGamma", "v1.5"),
    ]

    for name, tag in participants:
        test_participant_workflow(participant_name=name, submission_tag=tag)
        print("\n" + "=" * 60 + "\n")
        time.sleep(1)  # Small delay between submissions
