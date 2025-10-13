#!/usr/bin/env python
"""
Alert Creator for CNZ Platform
Creates alerts on the staging server after agent completes analysis
"""
import httpx
import os
from typing import Dict, Any, Optional
from datetime import datetime


class AlertCreator:
    """Creates alerts on CNZ platform"""

    def __init__(
        self,
        base_url: str = "https://stage-cnz.icmserver007.com",
        api_key: Optional[str] = None
    ):
        self.base_url = base_url
        self.api_key = api_key or os.getenv("CNZ_API_KEY", "cnz_xEZR7v2ETYz2DnVzrmqDYXprpPKOrNDA97GaD3yjdfA")

    async def create_alert(
        self,
        name: str,
        city_name: str,
        country_code: str,
        geoname_id: str,
        alert_type: str = "opportunity",
        category: Optional[str] = None,
        investment_min: Optional[float] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an alert on the CNZ platform

        Args:
            name: Alert name/title
            city_name: City name (e.g., "Bristol")
            country_code: Country code (e.g., "GB")
            geoname_id: GeoNames ID for the city (e.g., "Q21693433")
            alert_type: Type of alert (default: "opportunity")
            category: Category filter (e.g., "transport", "energy")
            investment_min: Minimum investment amount filter
            description: Additional description for the alert

        Returns:
            Response from the API
        """
        # Build city country code
        city_country_code = f"{city_name.lower()}-{country_code.upper()}"

        # Build alert payload
        payload = {
            "name": name,
            "criteria": {
                "type": alert_type,
                "conditions": {}
            },
            "geonameId": geoname_id,
            "cityCountryCode": city_country_code
        }

        # Add optional conditions
        if category:
            payload["criteria"]["conditions"]["category"] = category
        if investment_min is not None:
            payload["criteria"]["conditions"]["investment_min"] = investment_min
        if description:
            payload["description"] = description

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/v2/alerts",
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": self.api_key
                    }
                )
                response.raise_for_status()
                return {
                    "success": True,
                    "data": response.json(),
                    "status_code": response.status_code
                }
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "status_code": e.response.status_code
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def create_analysis_alert(
        self,
        query: str,
        results_summary: str,
        city_name: str = "Bristol",
        country_code: str = "GB",
        geoname_id: str = "Q21693433"
    ) -> Dict[str, Any]:
        """
        Create an alert based on data analysis results

        Args:
            query: The original query/question
            results_summary: Summary of the analysis results
            city_name: City analyzed (default: Bristol)
            country_code: Country code (default: GB)
            geoname_id: GeoNames ID (default: Bristol)

        Returns:
            Response from the API
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        alert_name = f"Data Analysis: {query[:50]}"
        description = f"Analysis completed at {timestamp}\n\nQuery: {query}\n\nResults: {results_summary}"

        return await self.create_alert(
            name=alert_name,
            city_name=city_name,
            country_code=country_code,
            geoname_id=geoname_id,
            alert_type="opportunity",
            description=description
        )


async def test_alert_creation():
    """Test alert creation"""
    creator = AlertCreator()

    # Test creating a simple alert
    result = await creator.create_alert(
        name="Test Alert - Data Analyst Agent",
        city_name="Bristol",
        country_code="GB",
        geoname_id="Q21693433",
        category="transport",
        investment_min=250000,
        description="This is a test alert created by the data analyst agent"
    )

    print("\nAlert Creation Result:")
    print("="*60)
    print(f"Success: {result.get('success')}")
    if result.get('success'):
        print(f"Status Code: {result.get('status_code')}")
        print(f"Response: {result.get('data')}")
    else:
        print(f"Error: {result.get('error')}")
    print("="*60)

    return result


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_alert_creation())
