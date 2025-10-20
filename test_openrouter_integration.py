#!/usr/bin/env python
"""
Quick test to verify OpenRouter integration works
"""
import asyncio
import sys
from pathlib import Path

# Add parent to path for openrouter_config
sys.path.append(str(Path(__file__).parent.parent))

async def test_import():
    """Test that imports work"""
    print("\n=== Testing Imports ===")
    try:
        from mindsdb_agent import MindsDBAgent
        print("[OK] MindsDBAgent imported successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to import MindsDBAgent: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_initialization():
    """Test that agent initializes"""
    print("\n=== Testing Agent Initialization ===")
    try:
        from mindsdb_agent import MindsDBAgent
        agent = MindsDBAgent(create_alerts=False)
        print(f"[OK] Agent initialized")
        print(f"[OK] Model: {agent.model}")
        print(f"[OK] Client type: {type(agent.client).__name__}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to initialize agent: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_basic_query():
    """Test a simple query (without database access)"""
    print("\n=== Testing Basic Query ===")
    try:
        from mindsdb_agent import MindsDBAgent
        agent = MindsDBAgent(create_alerts=False)

        # Simple query that doesn't require tools
        response = await agent.run("Say hello and tell me what you can help with in 2 sentences.")

        if response and len(response) > 20:
            print(f"[OK] Got response: {response[:100]}...")
            return True
        else:
            print(f"[WARNING] Response too short or empty: {response}")
            return False

    except Exception as e:
        print(f"[ERROR] Failed to run query: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("OpenRouter Integration Test for MindsDB Agent")
    print("="*60)

    results = []

    # Test 1: Imports
    results.append(("Imports", await test_import()))

    # Test 2: Initialization
    if results[0][1]:
        results.append(("Initialization", await test_initialization()))

    # Test 3: Basic Query
    if results[0][1] and (len(results) < 2 or results[1][1]):
        results.append(("Basic Query", await test_basic_query()))

    # Summary
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")

    all_passed = all(result[1] for result in results)
    print("\n" + "="*60)
    if all_passed:
        print("[SUCCESS] All tests passed!")
    else:
        print("[FAILURE] Some tests failed")
    print("="*60 + "\n")

    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
