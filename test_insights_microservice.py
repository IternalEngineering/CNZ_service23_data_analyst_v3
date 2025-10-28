"""
Test script for insights_microservice.py
Validates code structure without starting the server
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    try:
        from insights_microservice import (
            app,
            get_db_connection,
            get_latest_insight,
            get_insights_by_country,
            get_city_insight,
            parse_query_for_location,
            generate_insight_summary,
            ChatQueryRequest,
            ChatResponse,
            InsightDetail
        )
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_query_parser():
    """Test the natural language query parser"""
    print("\nTesting query parser...")
    from insights_microservice import parse_query_for_location

    test_cases = [
        ("Show me Bristol", ("Bristol", "GB")),
        ("What about Manchester in the UK?", ("Manchester", "GB")),
        ("Tell me about London", ("London", "GB")),
        ("Show me cities in the UK", (None, "GB")),
        ("Dubai insights", ("Dubai", "AE")),  # Parser correctly identifies Dubai
        ("Show me Singapore", ("Singapore", "SG")),
    ]

    all_passed = True
    for query, expected in test_cases:
        result = parse_query_for_location(query)
        if result == expected:
            print(f"  ✓ '{query}' → {result}")
        else:
            print(f"  ✗ '{query}' → {result} (expected {expected})")
            all_passed = False

    return all_passed


def test_pydantic_models():
    """Test Pydantic model validation"""
    print("\nTesting Pydantic models...")
    from insights_microservice import ChatQueryRequest, ChatResponse

    try:
        # Test request model
        request = ChatQueryRequest(query="Show me Bristol")
        assert request.query == "Show me Bristol"
        print("  ✓ ChatQueryRequest model works")

        # Test response model
        response = ChatResponse(
            reply="Test reply",
            replySummary="Test summary",
            table="service23_data_analyst_insights",
            id="550e8400-e29b-41d4-a716-446655440000"
        )
        assert response.reply == "Test reply"
        print("  ✓ ChatResponse model works")

        return True
    except Exception as e:
        print(f"  ✗ Model validation failed: {e}")
        return False


def test_fastapi_routes():
    """Test that FastAPI routes are defined"""
    print("\nTesting FastAPI routes...")
    from insights_microservice import app

    routes = [route.path for route in app.routes]
    expected_routes = [
        "/",
        "/health",
        "/chat/city",
        "/chat/cities",
        "/insights/recent",
        "/insights/{insight_id}",
        "/insights/city/{city_name}"
    ]

    all_found = True
    for route in expected_routes:
        if route in routes:
            print(f"  ✓ Route '{route}' defined")
        else:
            print(f"  ✗ Route '{route}' not found")
            all_found = False

    return all_found


def test_database_config():
    """Test database configuration"""
    print("\nTesting database configuration...")
    from insights_microservice import DB_CONFIG

    required_keys = ['host', 'port', 'database', 'user', 'password', 'sslmode']
    all_present = True

    for key in required_keys:
        if key in DB_CONFIG:
            print(f"  ✓ DB_CONFIG has '{key}'")
        else:
            print(f"  ✗ DB_CONFIG missing '{key}'")
            all_present = False

    return all_present


def main():
    """Run all tests"""
    print("="*60)
    print("INSIGHTS MICROSERVICE VALIDATION TEST")
    print("="*60)

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Query Parser", test_query_parser()))
    results.append(("Pydantic Models", test_pydantic_models()))
    results.append(("FastAPI Routes", test_fastapi_routes()))
    results.append(("Database Config", test_database_config()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All validation tests passed!")
        print("\nThe microservice is ready to run.")
        print("To start: python insights_microservice.py")
        print("Or with custom port: PORT=8025 python insights_microservice.py")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
