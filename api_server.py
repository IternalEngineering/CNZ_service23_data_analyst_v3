#!/usr/bin/env python
"""
FastAPI Server for Data Analyst Agent
Provides HTTP API access to the Claude SDK agent with PostgreSQL tools
"""
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Load environment variables - try multiple paths
from dotenv import load_dotenv

env_paths = [
    Path(__file__).parent.parent / '.env',  # ../crewai_service/.env
    Path(__file__).parent / '.env',          # ./data_analyst_agent/.env
    Path.cwd() / '.env',                     # current directory
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path, override=True)
        print(f"Loaded .env from: {env_path}")
        break

# Import agent
from mindsdb_agent import MindsDBAgent
from postgres_tool import execute_postgres_tool
from city_insights_analyzer import CityInsightsAnalyzer


# FastAPI app
app = FastAPI(
    title="Data Analyst Agent API",
    description="Claude SDK-powered data analyst agent with PostgreSQL and MindsDB access",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize Arize telemetry on startup
@app.on_event("startup")
async def startup_event():
    """Initialize Arize telemetry"""
    try:
        from arize_telemetry import initialize_telemetry
        if initialize_telemetry(project_name="Service23-DataAnalyst"):
            print("[OK] Arize telemetry initialized successfully")
        else:
            print("[SKIP] Arize telemetry not available")
    except Exception as e:
        print(f"[SKIP] Failed to initialize Arize telemetry: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Flush telemetry data on shutdown"""
    try:
        from arize_telemetry import flush_telemetry
        flush_telemetry()
        print("[OK] Telemetry data flushed")
    except Exception as e:
        print(f"Telemetry flush skipped: {e}")


# Request/Response models
class QueryRequest(BaseModel):
    query: str
    conversation_history: Optional[List[Dict]] = None


class QueryResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None


class AddColumnRequest(BaseModel):
    table: str
    column_name: str
    column_type: str
    default_value: Optional[str] = None


class PostgresResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Dict] = None
    error: Optional[str] = None


class CityInsightRequest(BaseModel):
    city: str
    country_code: str
    success_criteria: Optional[str] = None


class CityInsightResponse(BaseModel):
    success: bool
    insight_id: Optional[str] = None
    city: Optional[str] = None
    country_code: Optional[str] = None
    insight: Optional[Dict] = None
    alert_created: Optional[bool] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None


# Endpoints
@app.get("/")
async def root():
    """API info"""
    return {
        "name": "Data Analyst Agent API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "query": "/api/query (POST)",
            "add_column": "/api/postgres/add-column (POST)",
            "list_tables": "/api/postgres/tables (GET)",
            "city_insights": "/api/analyze/city-insights (POST)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "data_analyst_agent"
    }


@app.post("/api/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """
    Query the data analyst agent

    Example:
    ```
    {
        "query": "How many records are in service19_onboarding_data?"
    }
    ```
    """
    try:
        agent = MindsDBAgent()
        response = await agent.run(request.query, request.conversation_history)

        return QueryResponse(
            success=True,
            response=response
        )
    except Exception as e:
        return QueryResponse(
            success=False,
            error=str(e)
        )


@app.post("/api/postgres/add-column", response_model=PostgresResponse)
async def add_column(request: AddColumnRequest):
    """
    Add a column to a PostgreSQL table

    Example:
    ```
    {
        "table": "service19_onboarding_data",
        "column_name": "green_apples",
        "column_type": "INTEGER",
        "default_value": "0"
    }
    ```
    """
    try:
        result = await execute_postgres_tool(
            operation="add_column",
            table=request.table,
            column_name=request.column_name,
            column_type=request.column_type,
            default_value=request.default_value
        )

        if result.get("success"):
            return PostgresResponse(
                success=True,
                message=f"Column '{request.column_name}' added successfully",
                data=result
            )
        else:
            return PostgresResponse(
                success=False,
                error=result.get("error")
            )
    except Exception as e:
        return PostgresResponse(
            success=False,
            error=str(e)
        )


@app.get("/api/postgres/tables", response_model=PostgresResponse)
async def list_tables():
    """List all tables in the database"""
    try:
        result = await execute_postgres_tool(operation="list_tables")

        if result.get("success"):
            return PostgresResponse(
                success=True,
                data=result
            )
        else:
            return PostgresResponse(
                success=False,
                error=result.get("error")
            )
    except Exception as e:
        return PostgresResponse(
            success=False,
            error=str(e)
        )


@app.get("/api/postgres/schema/{table}")
async def get_table_schema(table: str):
    """Get schema for a specific table"""
    try:
        result = await execute_postgres_tool(
            operation="get_schema",
            table=table
        )

        if result.get("success"):
            return PostgresResponse(
                success=True,
                data=result
            )
        else:
            return PostgresResponse(
                success=False,
                error=result.get("error")
            )
    except Exception as e:
        return PostgresResponse(
            success=False,
            error=str(e)
        )


@app.post("/api/analyze/city-insights", response_model=CityInsightResponse)
async def analyze_city_insights(request: CityInsightRequest):
    """
    Analyze city data across disparate sources and generate insights

    This endpoint:
    1. Queries service6_onboarding_voice for success criteria
    2. Gathers data from multiple sources (opportunities, data_sources, etc.)
    3. Uses AI agent to connect information and generate insights
    4. Stores results in service23_data_analyst_insights table
    5. Creates an alert on the web platform

    Example:
    ```
    {
        "city": "Bristol",
        "country_code": "GB",
        "success_criteria": "Achieve net zero by 2030 through renewable energy"
    }
    ```
    """
    try:
        analyzer = CityInsightsAnalyzer()

        result = await analyzer.analyze_and_store(
            city=request.city,
            country_code=request.country_code,
            success_criteria=request.success_criteria,
            create_alert=True
        )

        if result.get("success"):
            return CityInsightResponse(
                success=True,
                insight_id=result.get("insight_id"),
                city=result.get("city"),
                country_code=result.get("country_code"),
                insight=result.get("insight"),
                alert_created=result.get("alert_created", False),
                timestamp=result.get("timestamp")
            )
        else:
            return CityInsightResponse(
                success=False,
                error=result.get("error", "Unknown error occurred")
            )

    except Exception as e:
        import traceback
        return CityInsightResponse(
            success=False,
            error=f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8023))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
