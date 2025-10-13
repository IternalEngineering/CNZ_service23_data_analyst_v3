#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
City Insights Analyzer - Gemini Version
Uses Google Gemini to analyze city data across disparate sources,
connecting information to generate insights relevant to success criteria.
Uses Gemini to avoid Claude context limit errors.
"""
import os
import sys
import asyncio
import uuid
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    # Only wrap if not already wrapped (check for _wrapped attribute)
    if not hasattr(sys.stdout, '_wrapped') and hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')
        sys.stdout._wrapped = True
    if not hasattr(sys.stderr, '_wrapped') and hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'ignore')
        sys.stderr._wrapped = True

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Import required tools
from postgres_direct_tool import PostgresDirectTool
from alert_creator import AlertCreator

# Import Google Gemini SDK
try:
    import google.generativeai as genai
except ImportError:
    print("ERROR: google-generativeai package not installed")
    print("Run: pip install google-generativeai")
    sys.exit(1)


class CityInsightsAnalyzerGemini:
    """Analyzer that uses Google Gemini to generate insights from disparate data sources"""

    def __init__(self, api_key: Optional[str] = None):
        # Use provided key or hardcoded key
        gemini_key = api_key or "AIzaSyBKlZKkvDAjUv8SqcwIQ_ElWOgqlaaoD6Q"

        # Configure Gemini
        genai.configure(api_key=gemini_key)

        # Use Gemini 2.5 Pro with large context window (2M tokens)
        self.model = genai.GenerativeModel(
            'gemini-2.5-pro',
            generation_config={
                'temperature': 0.7,
                'top_p': 0.95,
                'max_output_tokens': 8192,
            }
        )

        self.postgres = PostgresDirectTool()
        self.alert_creator = AlertCreator()

    def _get_tool_declarations(self):
        """Get tool declarations for Gemini function calling"""
        import google.ai.generativelanguage as glm

        return [
            glm.Tool(
                function_declarations=[
                    glm.FunctionDeclaration(
                        name="query_database",
                        description="""Query the PostgreSQL database to gather data.
Use this to:
- Query service6_onboarding_voice for success criteria (use text_responses column)
- Query service19_onboarding_agent_sources (use search_city column NOT 'city')
- Query service19_onboarding_data (use raw_data column NOT 'data_content')
- Join data across multiple tables
Always use LIMIT clauses to avoid overwhelming responses.""",
                        parameters=glm.Schema(
                            type=glm.Type.OBJECT,
                            properties={
                                "sql": glm.Schema(
                                    type=glm.Type.STRING,
                                    description="SQL query to execute. Must include LIMIT clause."
                                ),
                                "description": glm.Schema(
                                    type=glm.Type.STRING,
                                    description="Brief description of what this query does"
                                )
                            },
                            required=["sql", "description"]
                        )
                    )
                ]
            )
        ]

    async def _execute_tool(self, tool_name: str, tool_args: Dict) -> Dict[str, Any]:
        """Execute a tool call"""
        if tool_name == "query_database":
            sql = tool_args.get("sql", "")
            description = tool_args.get("description", "Query")

            # Safety check: require LIMIT
            if 'limit' not in sql.lower():
                return {
                    "success": False,
                    "error": "LIMIT clause required in all queries"
                }

            print(f"  Executing: {description}")
            print(f"  SQL: {sql[:100]}...")

            result = await self.postgres.query(sql)

            # Aggressively limit result size to prevent context overflow
            if result.get("success") and result.get("row_count", 0) > 0:
                print(f"  ✓ Found {result['row_count']} rows")

                # Truncate to max 5 rows and 3000 chars total
                truncated_data = result.get("data", [])[:5]

                # Convert UUIDs to strings for JSON serialization
                for row in truncated_data:
                    for key, value in row.items():
                        if hasattr(value, 'hex'):  # UUID object
                            row[key] = str(value)

                result = {
                    "success": True,
                    "row_count": result["row_count"],
                    "columns": result.get("columns", []),
                    "data": truncated_data,
                    "note": f"Result truncated to first 5 rows (of {result['row_count']} total) to save context"
                }

                # Further truncate if still too large
                result_str = str(result)
                if len(result_str) > 3000:
                    result = {
                        "success": True,
                        "row_count": result["row_count"],
                        "columns": result.get("columns", []),
                        "data": truncated_data[:2],
                        "note": f"Result heavily truncated (showing 2 of {result['row_count']} rows) due to size"
                    }

            return result

        return {"success": False, "error": f"Unknown tool: {tool_name}"}

    async def analyze_city(
        self,
        city: str,
        country_code: str,
        success_criteria: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze city data across disparate sources to generate insights

        Args:
            city: City name (e.g., "Bristol")
            country_code: ISO country code (e.g., "GB")
            success_criteria: Optional success criteria. If not provided, will query from database

        Returns:
            Dict containing insight data and metadata
        """
        print(f"\n{'='*60}")
        print(f"Analyzing: {city}, {country_code}")
        print(f"{'='*60}\n")

        # Build analysis prompt
        if success_criteria:
            criteria_text = f"Success criteria: {success_criteria}"
        else:
            criteria_text = "First, query the database to find success criteria from service6_onboarding_voice table"

        system_instruction = f"""You are a data analyst agent analyzing city data to generate actionable insights.

CRITICAL: You have a MAXIMUM of 6-8 queries. Be efficient and focused.

Your task:
1. Gather data from multiple sources about {city}, {country_code}
2. {criteria_text}
3. Connect information across disparate data sources
4. Generate insights that are relevant to the success criteria
5. Provide concrete recommendations

Available tables and correct columns to query:
- service6_onboarding_voice - Contains success criteria (columns: id, user_id, text_responses, data_collection, challenges, created_at)
- service19_onboarding_agent_sources - Source metadata (columns: id, search_city, country_code, dataset_title, download_urls, data_quality_score, openai_quality_score, created_at)
- service19_onboarding_data - Collected city data (columns: data_id, source_id, download_url, download_success, data_format, file_size_bytes, record_count, raw_data, completeness_score, error_details)
- opportunities - Investment opportunities data
- data_sources - Available data sources

IMPORTANT COLUMN NAMES:
- service6_onboarding_voice: Use 'text_responses' (JSONB) - contains success_criteria, data_collection, challenges
- service19_onboarding_agent_sources: Use 'search_city' NOT 'city'
- service19_onboarding_agent_sources: Use 'id' as primary key (NOT 'source_id')
- service19_onboarding_data: Use 'raw_data' (JSONB) NOT 'data_content'
- service19_onboarding_data: Use 'source_id' as foreign key to service19_onboarding_agent_sources.id

DATA SIZE MANAGEMENT (CRITICAL):
- NEVER query the full 'raw_data' column directly (it can be megabytes of GeoJSON!)
- Use JSON extraction functions to get summaries only:
  * jsonb_array_length(raw_data->'features') - count features without retrieving them
  * raw_data->'features'->0 - get ONE sample feature
  * raw_data->'features'->0->'properties' - get sample properties
  * raw_data->'features'->0->'properties'->>'field_name' - extract specific field
- Example GOOD query:
  SELECT dataset_title, record_count,
         jsonb_array_length(raw_data->'features') as feature_count,
         raw_data->'features'->0->'properties'->>'Plant_Name' as sample_name
  FROM service19_onboarding_data WHERE source_id = '...' LIMIT 1
- Example BAD query (causes context overflow):
  SELECT raw_data FROM service19_onboarding_data LIMIT 5  ❌

EFFICIENCY RULES:
- Query AT MOST 5 times before concluding
- Each query must return max 5 rows (use LIMIT 5)
- Focus on the MOST relevant data sources only
- Don't query if you already have enough information
- Conclude as soon as you have 2-3 data points

Your final response should be structured JSON:
{{
    "insight_summary": "Brief 1-2 sentence summary",
    "detailed_analysis": "Comprehensive analysis connecting data sources",
    "data_sources_used": ["table1", "table2", ...],
    "confidence_score": 0.85,
    "recommendations": ["Recommendation 1", "Recommendation 2", ...]
}}"""

        user_message = f"""Analyze {city}, {country_code} and provide insights.

IMPORTANT: Be EFFICIENT - query at most 3-5 times, then conclude with your analysis.

Quick workflow:
1. Query service6_onboarding_voice for success criteria (text_responses->>'success_criteria') LIMIT 1
2. Query service19_onboarding_agent_sources for available data WHERE search_city='{city}' LIMIT 5
3. Query service19_onboarding_data for summaries (record_count, data_format, feature counts) LIMIT 3
4. If specific data values needed: Extract using JSON functions (raw_data->'features'->0->'properties') LIMIT 1
5. STOP and provide your JSON analysis

CRITICAL COLUMN NAMES:
- service6_onboarding_voice.text_responses (JSONB) - NOT 'question_text' or 'response_text'
- service19_onboarding_agent_sources.search_city - NOT 'city'
- service19_onboarding_agent_sources.id (primary key) - NOT 'source_id' as column name
- service19_onboarding_data.raw_data (JSONB) - NOT 'data_content'
- service19_onboarding_data.source_id (foreign key to service19_onboarding_agent_sources.id)

CRITICAL DATA SIZE RULES:
- NEVER SELECT raw_data without JSON extraction functions (causes context overflow!)
- Use jsonb_array_length(raw_data->'features') to count instead of retrieving
- Extract single samples with raw_data->'features'->0->'properties'
- Use LIMIT 1 when querying tables with JSONB columns

Remember: Use LIMIT in ALL queries. Query at most 5 times total."""

        # Create chat session with tools
        tools = self._get_tool_declarations()

        # Start chat with system instruction
        chat = self.model.start_chat(enable_automatic_function_calling=False)

        max_iterations = 8
        iteration = 0

        # Send initial message with system instruction prepended
        full_prompt = f"{system_instruction}\n\n{user_message}"

        try:
            response = chat.send_message(full_prompt, tools=tools)
        except Exception as e:
            return {
                "success": False,
                "error": f"Initial message failed: {e}",
                "city": city,
                "country_code": country_code
            }

        while iteration < max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")

            try:
                # Check if we have function calls
                function_calls = []
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_calls.append(part.function_call)

                if function_calls:
                    # Execute all function calls
                    function_responses = []
                    for fc in function_calls:
                        print(f"Agent calling: {fc.name}")
                        result = await self._execute_tool(fc.name, dict(fc.args))

                        # Create function response
                        function_responses.append(
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=fc.name,
                                    response={'result': result}
                                )
                            )
                        )

                    # Send function responses back
                    response = chat.send_message(function_responses, tools=tools)

                else:
                    # No function calls, check for text response
                    if response.text:
                        final_response = response.text
                        print(f"\n{'='*60}")
                        print("Analysis Complete")
                        print(f"{'='*60}\n")

                        # Parse the response (expect JSON)
                        try:
                            # Try to extract JSON from the response
                            if "```json" in final_response:
                                json_start = final_response.find("```json") + 7
                                json_end = final_response.find("```", json_start)
                                json_str = final_response[json_start:json_end].strip()
                            elif "{" in final_response and "}" in final_response:
                                json_start = final_response.find("{")
                                json_end = final_response.rfind("}") + 1
                                json_str = final_response[json_start:json_end]
                            else:
                                json_str = final_response

                            insight_data = json.loads(json_str)
                        except json.JSONDecodeError:
                            # Fallback if not JSON
                            insight_data = {
                                "insight_summary": final_response[:200],
                                "detailed_analysis": final_response,
                                "data_sources_used": ["unknown"],
                                "confidence_score": 0.5,
                                "recommendations": []
                            }

                        return {
                            "success": True,
                            "city": city,
                            "country_code": country_code,
                            "insight": insight_data,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    else:
                        print("No text or function calls in response")
                        break

            except Exception as e:
                print(f"Error in iteration {iteration}: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(2)
                break

        # Max iterations reached
        return {
            "success": False,
            "error": "Max iterations reached without completion",
            "city": city,
            "country_code": country_code
        }

    async def store_insight(self, insight_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store insight in database

        Args:
            insight_data: Insight data from analyze_city()

        Returns:
            Result dict with insight_id
        """
        if not insight_data.get("success"):
            return {"success": False, "error": "Cannot store failed insight"}

        insight = insight_data["insight"]
        insight_id = str(uuid.uuid4())

        sql = """
        INSERT INTO service23_data_analyst_insights (
            id, city, country_code, success_criteria,
            insight_summary, detailed_analysis,
            data_sources_used, confidence_score, recommendations,
            created_at, alert_sent
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), FALSE
        )
        RETURNING id
        """

        try:
            # Connect and insert
            await self.postgres.connect()

            params = [
                insight_id,
                insight_data["city"],
                insight_data["country_code"],
                insight.get("success_criteria", ""),
                insight.get("insight_summary", "")[:500],
                insight.get("detailed_analysis", ""),
                json.dumps(insight.get("data_sources_used", [])),
                insight.get("confidence_score", 0.5),
                json.dumps(insight.get("recommendations", []))
            ]

            result = await self.postgres.query(sql, params)

            if result.get("success"):
                print(f"✓ Stored insight with ID: {insight_id}")
                return {
                    "success": True,
                    "insight_id": insight_id
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error storing insight")
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to store insight: {str(e)}"
            }

    async def create_insight_alert(
        self,
        city: str,
        country_code: str,
        insight_data: Dict[str, Any],
        insight_id: str
    ) -> Dict[str, Any]:
        """
        Create an alert on the web platform

        Args:
            city: City name
            country_code: Country code
            insight_data: Insight data
            insight_id: UUID of stored insight

        Returns:
            Alert creation result
        """
        insight = insight_data.get("insight", {})

        alert_name = f"Data Insight: {city}"
        description = f"""Data Analyst Insight Generated (Gemini)

Summary: {insight.get('insight_summary', 'N/A')}

Confidence: {insight.get('confidence_score', 0.5):.0%}

Insight ID: {insight_id}

Top Recommendations:
{chr(10).join('• ' + rec for rec in insight.get('recommendations', [])[:3])}

View full analysis in the database (service23_data_analyst_insights table)."""

        # Default geoname_id for Bristol (should be looked up dynamically in production)
        geoname_id = "Q21693433" if city.lower() == "bristol" else "Q000000"

        result = await self.alert_creator.create_alert(
            name=alert_name,
            city_name=city,
            country_code=country_code,
            geoname_id=geoname_id,
            alert_type="opportunity",
            category="data_insights",
            description=description
        )

        if result.get("success"):
            # Update database to mark alert as sent
            update_sql = """
            UPDATE service23_data_analyst_insights
            SET alert_sent = TRUE
            WHERE id = $1
            """
            await self.postgres.query(update_sql, [insight_id])

        return result

    async def analyze_and_store(
        self,
        city: str,
        country_code: str,
        success_criteria: Optional[str] = None,
        create_alert: bool = True
    ) -> Dict[str, Any]:
        """
        Complete workflow: analyze, store, and alert

        Args:
            city: City name
            country_code: Country code
            success_criteria: Optional success criteria
            create_alert: Whether to create web alert

        Returns:
            Complete result dict
        """
        try:
            # Step 1: Analyze
            print("Step 1: Analyzing city data with Gemini...")
            insight_data = await self.analyze_city(city, country_code, success_criteria)

            if not insight_data.get("success"):
                return insight_data

            # Step 2: Store
            print("\nStep 2: Storing insight in database...")
            store_result = await self.store_insight(insight_data)

            if not store_result.get("success"):
                return store_result

            insight_id = store_result["insight_id"]

            # Step 3: Create alert
            alert_result = {"success": False, "message": "Alert creation skipped"}
            if create_alert:
                print("\nStep 3: Creating web alert...")
                alert_result = await self.create_insight_alert(
                    city, country_code, insight_data, insight_id
                )

                if alert_result.get("success"):
                    print("✓ Alert created successfully")
                else:
                    print(f"⚠ Alert creation failed: {alert_result.get('error')}")

            # Return complete result
            return {
                "success": True,
                "insight_id": insight_id,
                "city": city,
                "country_code": country_code,
                "insight": insight_data["insight"],
                "alert_created": alert_result.get("success", False),
                "timestamp": insight_data["timestamp"]
            }

        except Exception as e:
            import traceback
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        finally:
            await self.postgres.close()


async def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze city data with Gemini and generate insights")
    parser.add_argument("--city", required=True, help="City name (e.g., Bristol)")
    parser.add_argument("--country-code", required=True, help="Country code (e.g., GB)")
    parser.add_argument("--success-criteria", help="Optional success criteria")
    parser.add_argument("--no-alert", action="store_true", help="Skip alert creation")

    args = parser.parse_args()

    analyzer = CityInsightsAnalyzerGemini()

    result = await analyzer.analyze_and_store(
        city=args.city,
        country_code=args.country_code,
        success_criteria=args.success_criteria,
        create_alert=not args.no_alert
    )

    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)
    print(json.dumps(result, indent=2))
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
