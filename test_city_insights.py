#!/usr/bin/env python
"""
Test script for city insights analyzer
Tests the complete flow: analyze -> store -> alert
"""
import asyncio
import sys
from city_insights_analyzer import CityInsightsAnalyzer


async def test_analyzer():
    """Test the city insights analyzer"""
    print("\n" + "="*60)
    print("Testing City Insights Analyzer")
    print("="*60)

    # Test parameters
    city = "Bristol"
    country_code = "GB"
    success_criteria = "Achieve net zero by 2030 through renewable energy"

    print(f"\nTest Parameters:")
    print(f"  City: {city}")
    print(f"  Country: {country_code}")
    print(f"  Success Criteria: {success_criteria}")

    # Create analyzer
    analyzer = CityInsightsAnalyzer()

    # Run analysis
    print("\n" + "-"*60)
    print("Starting Analysis...")
    print("-"*60)

    try:
        result = await analyzer.analyze_and_store(
            city=city,
            country_code=country_code,
            success_criteria=success_criteria,
            create_alert=True
        )

        print("\n" + "="*60)
        print("RESULT")
        print("="*60)

        if result.get("success"):
            print("\n✓ Analysis completed successfully!")
            print(f"\nInsight ID: {result.get('insight_id')}")
            print(f"Timestamp: {result.get('timestamp')}")
            print(f"Alert Created: {result.get('alert_created', False)}")

            insight = result.get("insight", {})
            print(f"\n--- Insight Summary ---")
            print(insight.get("insight_summary", "N/A"))

            print(f"\n--- Confidence Score ---")
            print(f"{insight.get('confidence_score', 0):.0%}")

            print(f"\n--- Data Sources Used ---")
            for source in insight.get("data_sources_used", []):
                print(f"  • {source}")

            print(f"\n--- Recommendations ---")
            for i, rec in enumerate(insight.get("recommendations", []), 1):
                print(f"  {i}. {rec}")

            print(f"\n--- Detailed Analysis ---")
            print(insight.get("detailed_analysis", "N/A")[:500])
            if len(insight.get("detailed_analysis", "")) > 500:
                print("... (truncated)")

            return True

        else:
            print("\n✗ Analysis failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"\n✗ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_analyzer())
    sys.exit(0 if success else 1)
