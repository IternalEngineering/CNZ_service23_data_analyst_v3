#!/usr/bin/env python
"""
Export Tool for MindsDB Agent
Saves large query results to files instead of returning to context
"""
import csv
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class ExportTool:
    """Tool to export query results to files"""

    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def export_to_csv(
        self,
        data: List[List[Any]],
        columns: List[str],
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export query results to CSV file

        Args:
            data: Query result data (list of rows)
            columns: Column names
            filename: Optional custom filename

        Returns:
            Export summary
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"query_results_{timestamp}.csv"

        filepath = self.output_dir / filename

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(columns)
                # Write data
                writer.writerows(data)

            return {
                "success": True,
                "filepath": str(filepath.absolute()),
                "rows_exported": len(data),
                "columns": len(columns),
                "format": "csv"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def export_to_json(
        self,
        data: List[List[Any]],
        columns: List[str],
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export query results to JSON file

        Args:
            data: Query result data (list of rows)
            columns: Column names
            filename: Optional custom filename

        Returns:
            Export summary
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"query_results_{timestamp}.json"

        filepath = self.output_dir / filename

        try:
            # Convert rows to dictionaries
            records = [dict(zip(columns, row)) for row in data]

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "exported_at": datetime.now().isoformat(),
                        "row_count": len(data),
                        "column_count": len(columns),
                        "columns": columns
                    },
                    "data": records
                }, f, indent=2, default=str)

            return {
                "success": True,
                "filepath": str(filepath.absolute()),
                "rows_exported": len(data),
                "columns": len(columns),
                "format": "json"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def should_export(self, row_count: int, threshold: int = 50) -> bool:
        """
        Determine if results should be exported instead of returned

        Args:
            row_count: Number of rows in result
            threshold: Max rows to return to context (default: 50)

        Returns:
            True if should export, False otherwise
        """
        return row_count > threshold


def get_export_tool_definition() -> Dict[str, Any]:
    """
    Get tool definition for OpenAI/LiteLLM SDK

    Returns:
        Tool definition dict
    """
    return {
        "type": "function",
        "function": {
            "name": "export_query_results",
            "description": """Export large query results to a file instead of returning them to the conversation.

Use this tool when:
- Query returns more than 50 rows
- Results contain large text fields
- You want to save results for later analysis

The tool will save results as CSV or JSON and return only a summary.""",
            "parameters": {
                "type": "object",
                "properties": {
                "data": {
                    "type": "array",
                    "description": "Query result data (array of rows)",
                    "items": {}
                },
                "columns": {
                    "type": "array",
                    "description": "Column names",
                    "items": {
                        "type": "string"
                    }
                },
                "filename": {
                    "type": "string",
                    "description": "Custom filename (optional). Should include .csv or .json extension"
                },
                "format": {
                    "type": "string",
                    "enum": ["csv", "json"],
                    "description": "Export format (csv or json)"
                }
            },
            "required": ["data", "columns", "format"]
            }
        }
    }


async def execute_export_tool(
    data: List[List[Any]],
    columns: List[str],
    format: str = "csv",
    filename: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute export tool operation

    Args:
        data: Query result data
        columns: Column names
        format: Export format (csv or json)
        filename: Optional custom filename

    Returns:
        Export summary
    """
    tool = ExportTool()

    if format == "json":
        result = tool.export_to_json(data, columns, filename)
    else:
        result = tool.export_to_csv(data, columns, filename)

    # Return concise summary for context
    if result.get("success"):
        return {
            "success": True,
            "message": f"Successfully exported {result['rows_exported']} rows to {result['filepath']}",
            "filepath": result['filepath'],
            "row_count": result['rows_exported']
        }
    else:
        return {
            "success": False,
            "error": result.get("error", "Export failed")
        }
