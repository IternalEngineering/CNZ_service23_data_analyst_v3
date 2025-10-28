#!/usr/bin/env python
"""
MindsDB Data Analyst Agent
OpenRouter-powered agent that can query SERVICE19 onboarding data via MindsDB
Uses LiteLLM for unified model access across providers
"""
import os
import sys
import asyncio
import time
from pathlib import Path
from typing import List, Dict, Any

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Import unified OpenRouter client
sys.path.append(str(Path(__file__).parent.parent))
from openrouter_config import get_llm_client

# Import LiteLLM for OpenRouter access
try:
    from litellm import completion
except ImportError:
    print("ERROR: litellm package not installed")
    print("Run: pip install litellm")
    sys.exit(1)

# Import MindsDB tool
from mindsdb_tool import execute_mindsdb_tool, get_mindsdb_tool_definition
from postgres_direct_tool import execute_postgres_direct_tool, get_postgres_direct_tool_definition

# Import PostgreSQL tool
from postgres_tool import execute_postgres_tool, get_postgres_tool_definition

# Import Alert Creator
from alert_creator import AlertCreator

# Import Export Tool
from export_tool import execute_export_tool, get_export_tool_definition


class MindsDBAgent:
    """OpenRouter-powered agent with MindsDB tool access via LiteLLM"""

    def __init__(self, create_alerts: bool = False):
        # Initialize unified LLM client for data analysis via OpenRouter
        self.client = get_llm_client(task_type="analysis", temperature=0.7, max_tokens=4096)
        self.model = self.client.model

        print(f"\n[*] Using model: {self.model}")
        print(f"[*] Estimated cost: ${self.client.estimated_cost}/1M tokens\n")

        # Tool definitions
        self.mindsdb_tool = get_mindsdb_tool_definition()
        self.export_tool = get_export_tool_definition()
        self.postgres_direct_tool = get_postgres_direct_tool_definition()
        self.tools = [self.mindsdb_tool, self.postgres_direct_tool, self.export_tool]

        # Alert creator (disabled by default)
        self.create_alerts = create_alerts
        self.alert_creator = AlertCreator() if create_alerts else None

        # System prompt
        self.system_prompt = """You are a data analyst agent with access to SERVICE19 onboarding data via MindsDB.

Your capabilities:
- Query city data collection results from urbanzero_postgres.service19_onboarding_data
- Join with urbanzero_postgres.service19_onboarding_agent_sources for city information
- Analyze data source URLs, fetch success rates, and file types
- Provide insights on data quality and collection issues

IMPORTANT - 1M Context Window Enabled:
- You have access to 1M token context window (5x larger than standard)
- raw_data and error_details CAN be queried BUT require LIMIT (max 10 rows)
- Always use LIMIT clauses when querying large JSON columns
- Still prefer aggregate queries when possible for performance

The service19_onboarding_data table columns (use these names exactly):
- data_id, source_id, download_url, download_timestamp
- download_success (boolean), http_status_code, data_format
- file_size_bytes, record_count, error_message
- raw_data, error_details (requires LIMIT ≤ 10)

The service19_onboarding_agent_sources table columns:
- source_id (primary key), city_name, country, source_type, source_url
- NOTE: When joining, the sources table does NOT have a matching column in lowercase,
  use the exact column names as listed above

Example safe queries:

1. Aggregate query:
SELECT s.city_name, COUNT(*) as total,
       SUM(CASE WHEN d.download_success THEN 1 ELSE 0 END) as successful
FROM urbanzero_postgres.service19_onboarding_data d
JOIN urbanzero_postgres.service19_onboarding_agent_sources s ON d.source_id = s.source_id
GROUP BY s.city_name
LIMIT 20;

2. Extract specific JSON fields (safe):
SELECT data_id, source_id,
       raw_data->>'parse_error' as parse_error,
       LEFT(raw_data->>'raw_content', 200) as content_preview
FROM urbanzero_postgres.service19_onboarding_data
WHERE raw_data->>'parse_error' IS NOT NULL
LIMIT 10;

3. Search within JSON:
SELECT data_id,
       raw_data->>'parse_error' as error_type
FROM urbanzero_postgres.service19_onboarding_data
WHERE raw_data::text LIKE '%Expected%fields%'
LIMIT 10;

JSON Querying Tips:
- Use -> to get JSON object, ->> to get text value
- Use LEFT() or SUBSTRING() to limit text size
- Search with LIKE or ~ (regex) on raw_data::text
- Extract only the fields you need, not the whole JSON

CRITICAL - NEVER query raw_data::text without LEFT() or specific field extraction:
❌ WRONG: SELECT raw_data::text FROM ...
❌ WRONG: SELECT raw_data as full_data FROM ...
✅ CORRECT: SELECT raw_data->>'field_name' as field FROM ...
✅ CORRECT: SELECT LEFT(raw_data::text, 500) as preview FROM ...
✅ CORRECT: SELECT raw_data->'geometry'->'coordinates' as coords FROM ...

For GeoJSON data (zebra crossings, locations, etc):
- Extract geometry: raw_data->'geometry'
- Get coordinates: raw_data->'geometry'->'coordinates'
- Get properties: raw_data->'properties'->>'name'
- Get type: raw_data->>'type'
- NEVER select the full raw_data column!

CRITICAL - Managing Large Results:
- If query returns >50 rows, use export_query_results tool
- Export tool saves data to CSV/JSON file and returns only summary
- This prevents context overflow and rate limits
- After exporting, tell user where file was saved

Example export workflow:
1. Execute query with query_mindsdb
2. If row_count > 50, immediately use export_query_results
3. Pass the data and columns from query result to export tool
4. Tell user: "Exported 150 rows to results/zebra_crossings_20241006.csv"

When analyzing data, provide clear insights and actionable recommendations."""

    async def run(self, user_message: str, conversation_history: List[Dict] = None) -> str:
        """
        Run the agent with a user message

        Args:
            user_message: User's question or request
            conversation_history: Previous conversation messages

        Returns:
            Agent's response
        """
        messages = conversation_history or []
        messages.append({
            "role": "user",
            "content": user_message
        })

        print(f"\n{'='*60}")
        print(f"User: {user_message}")
        print(f"{'='*60}\n")

        while True:
            # Call LLM with tools via OpenRouter (with rate limit retry)
            max_retries = 5
            for retry in range(max_retries):
                try:
                    response = completion(
                        model=self.model,
                        messages=[{"role": "system", "content": self.system_prompt}] + messages,
                        tools=self.tools,
                        max_tokens=4096,
                        temperature=0.7,
                        drop_params=True  # Drop unsupported params for OpenRouter
                    )
                    break  # Success, exit retry loop

                except Exception as e:
                    # Handle rate limits and other API errors
                    if 'rate' in str(e).lower() or 'limit' in str(e).lower():
                        if retry < max_retries - 1:
                            wait_time = (2 ** retry) * 3  # Exponential backoff: 3s, 6s, 12s, 24s, 48s
                            print(f"\n[WARNING] Rate limit hit. Waiting {wait_time}s before retry {retry + 1}/{max_retries}...")
                            time.sleep(wait_time)
                        else:
                            print(f"\n[ERROR] Rate limit exceeded after {max_retries} retries")
                            raise e
                    else:
                        # Re-raise non-rate-limit errors immediately
                        raise e

            # Get the response message
            response_message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason

            print(f"Finish reason: {finish_reason}")

            # Check if LLM wants to use a tool
            if finish_reason == "tool_calls" and response_message.tool_calls:
                # Extract tool calls and text
                tool_calls = response_message.tool_calls
                assistant_text = response_message.content or ""

                # Print assistant's thinking
                if assistant_text:
                    print(f"Assistant: {assistant_text}\n")

                # Execute tools
                tool_results = []
                for tool_call in tool_calls:
                    print(f"Using tool: {tool_call.function.name}")
                    print(f"Parameters: {tool_call.function.arguments}")

                    # Parse arguments (LiteLLM returns JSON string)
                    import json
                    if isinstance(tool_call.function.arguments, str):
                        arguments = json.loads(tool_call.function.arguments)
                    else:
                        arguments = tool_call.function.arguments

                    # Execute appropriate tool
                    if tool_call.function.name == "query_mindsdb":
                        result = await execute_mindsdb_tool(**arguments)
                        result_str = str(result)
                    elif tool_call.function.name == "query_postgres_direct":
                        result = await execute_postgres_direct_tool(**arguments)
                        print(f"Direct PostgreSQL Result: {result.get('success', False)}")
                        if result.get('row_count'):
                            print(f"Rows: {result['row_count']}")
                        
                        # Limit result size
                        result_str = str(result)
                        if len(result_str) > 10000:
                            result_summary = {
                                "success": result.get("success"),
                                "row_count": result.get("row_count"),
                                "columns": result.get("columns"),
                                "data_sample": result.get("data", [])[:5],
                                "note": "Result truncated. Use LIMIT in query to control size."
                            }
                            result_str = str(result_summary)

                        print(f"Result: {result.get('success', False)}")
                        if result.get('row_count'):
                            print(f"Rows: {result['row_count']}")

                        # Limit result size to avoid token limits
                        result_str = str(result)
                        if len(result_str) > 10000:
                            # Truncate large results
                            result_summary = {
                                "success": result.get("success"),
                                "row_count": result.get("row_count"),
                                "columns": result.get("columns"),
                                "data_sample": result.get("data", [])[:3] if result.get("data") else [],
                                "note": f"Result truncated (showed 3/{result.get('row_count', 0)} rows). Use export_query_results tool to save full dataset."
                            }
                            result_str = str(result_summary)

                    elif tool_call.function.name == "export_query_results":
                        result = await execute_export_tool(**arguments)
                        print(f"Export result: {result.get('success', False)}")
                        if result.get('row_count'):
                            print(f"Exported {result['row_count']} rows to {result.get('filepath')}")
                        result_str = str(result)

                    else:
                        result_str = str({"error": f"Unknown tool: {tool_call.function.name}"})

                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": result_str
                    })

                # Add assistant message with tool calls to conversation
                messages.append({
                    "role": "assistant",
                    "content": assistant_text,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in tool_calls
                    ]
                })

                # Add tool results
                messages.extend(tool_results)

                # Prune conversation to prevent context bloat
                # Keep pairs together: assistant (tool_use) + user (tool_result)
                if len(messages) > 12:
                    # Keep first message (user query)
                    # Then keep last N complete pairs (assistant + user)
                    # Messages come in pattern: user, assistant, user, assistant, user...
                    # After tool use: assistant (with tool_use), user (with tool_result)

                    # Keep first user message + last 10 messages (5 pairs)
                    # Ensure we start on an assistant message to maintain pairing
                    remaining = messages[-10:]
                    if remaining and remaining[0].get("role") == "user":
                        # Skip the orphaned user message
                        remaining = messages[-9:]

                    messages = [messages[0]] + remaining

                print()  # Blank line for readability

            else:
                # Final response without tool use
                final_response = response_message.content or ""
                print(f"{'='*60}")
                print(f"Assistant: {final_response}")
                print(f"{'='*60}\n")

                # Create alert if enabled
                if self.create_alerts and self.alert_creator:
                    print("\nCreating alert on CNZ platform...")
                    alert_result = await self.alert_creator.create_analysis_alert(
                        query=user_message,
                        results_summary=final_response[:500]  # Limit to 500 chars
                    )
                    if alert_result.get("success"):
                        print("[OK] Alert created successfully!")
                    else:
                        print(f"[WARNING] Alert creation failed: {alert_result.get('error')}")

                return final_response

    async def interactive_mode(self):
        """Run agent in interactive mode"""
        print("\n" + "="*60)
        print("MindsDB Data Analyst Agent")
        print("="*60)
        print("\nI can help you analyze SERVICE19 onboarding data!")
        print("Ask me questions like:")
        print("  - How many records are in the database?")
        print("  - Show me some sample data")
        print("  - What's the success rate for data fetches?")
        print("  - Show me failed fetches")
        print("  - What file types were collected?")
        print("\nType 'quit' to exit.\n")

        conversation_history = []

        while True:
            try:
                user_input = input("You: ").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break

                if not user_input:
                    continue

                response = await self.run(user_input, conversation_history)

                # Add to conversation history
                conversation_history.append({
                    "role": "user",
                    "content": user_input
                })
                conversation_history.append({
                    "role": "assistant",
                    "content": response
                })

            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                import traceback
                traceback.print_exc()


async def main():
    """Main entry point"""
    # Check for --no-alerts flag
    create_alerts = "--no-alerts" not in sys.argv
    args = [arg for arg in sys.argv[1:] if arg != "--no-alerts"]

    agent = MindsDBAgent(create_alerts=create_alerts)

    # Check if running in interactive mode or with a single query
    if len(args) > 0:
        # Single query mode
        query = " ".join(args)
        await agent.run(query)
    else:
        # Interactive mode
        await agent.interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())
