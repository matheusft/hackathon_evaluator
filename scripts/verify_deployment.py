#!/usr/bin/env python3
"""
Deployment Verification Script
==============================

Verifies that the application can start successfully in a production-like environment.
"""

import os
import sys
import traceback
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_imports() -> bool:
    """Test all critical imports."""
    print("🔍 Testing imports...")

    try:
        from src.core.test_data_provider import TestDataProvider  # noqa: F401
        print("  ✅ test_data_provider")
    except Exception as e:
        print(f"  ❌ test_data_provider: {e}")
        return False

    try:
        from src.core.leaderboard_manager import LeaderboardManager  # noqa: F401
        print("  ✅ leaderboard_manager (import only)")
    except Exception as e:
        print(f"  ❌ leaderboard_manager: {e}")
        return False

    try:
        from src.core.evaluator import EvaluationEngine  # noqa: F401
        print("  ✅ evaluator")
    except Exception as e:
        print(f"  ❌ evaluator: {e}")
        return False

    try:
        from config.config_manager import load_config  # noqa: F401
        print("  ✅ config_manager")
    except Exception as e:
        print(f"  ❌ config_manager: {e}")
        return False

    return True


def test_app_creation() -> bool:
    """Test app creation with minimal environment."""
    print("\n🏗️  Testing app creation...")

    # Set minimal required environment
    os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    os.environ.setdefault("ENVIRONMENT", "production")

    try:
        from app import create_app
        create_app(
            config_override={
                "DATABASE_URL": "postgresql://test:test@localhost:5432/test",
                "SECRET_KEY": "test-secret-key",
                "DEBUG": False,
            }
        )
        print("  ✅ App created successfully")
        return True
    except Exception as e:
        print(f"  ❌ App creation failed: {e}")
        traceback.print_exc()
        return False


def test_wsgi_entry() -> bool:
    """Test WSGI entry point."""
    print("\n🚀 Testing WSGI entry point...")

    # Set required environment variables
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["ENVIRONMENT"] = "production"

    try:
        import wsgi  # noqa: F401
        if hasattr(wsgi, "app"):
            print("  ✅ WSGI app object available")
            return True
        else:
            print("  ❌ WSGI app object not found")
            return False
    except Exception as e:
        print(f"  ❌ WSGI entry failed: {e}")
        traceback.print_exc()
        return False


def check_required_files() -> bool:
    """Check that all required files exist."""
    print("\n📁 Checking required files...")

    required_files = [
        "app.py",
        "wsgi.py",
        "requirements.txt",
        "render.yaml",
        "src/core/evaluator.py",
        "src/core/leaderboard_manager.py",
        "src/core/test_data_provider.py",
        "config/config_manager.py",
        "templates/leaderboard.html",
    ]

    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing_files.append(file_path)

    return len(missing_files) == 0


def main():
    """Run all deployment verification tests."""
    print("🔧 Deployment Verification")
    print("=" * 40)

    tests = [
        ("Required Files", check_required_files),
        ("Imports", test_imports),
        ("App Creation", test_app_creation),
        ("WSGI Entry", test_wsgi_entry),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 40)
    print("📊 SUMMARY")
    print("=" * 40)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 All tests passed! Deployment should be successful.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the issues above before deploying.")
        sys.exit(1)


if __name__ == "__main__":
    main()