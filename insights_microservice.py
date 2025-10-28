"""
City Insights Microservice API
FastAPI service for real-time access to cached city insights from service23_data_analyst_insights table
"""

import os
import uuid
from datetime import datetime
from typing import Dict, Optional, List, Any
from enum import Enum
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
env_paths = [
    Path(__file__).parent.parent / '.env',
    Path(__file__).parent / '.env',
    Path.cwd() / '.env',
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path, override=True)
        print(f"Loaded .env from: {env_path}")
        break

# PostgreSQL configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'urbanzero-db.c5qeo4ayy5u5.eu-west-2.rds.amazonaws.com'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'urbanzero-db'),
    'user': os.getenv('DB_USER', 'urbanzero_app'),
    'password': os.getenv('DB_PASSWORD', 'UrbanZero2024$Secure'),
    'sslmode': 'require'
}

# FastAPI app
app = FastAPI(
    title="City Insights Microservice",
    description="Real-time access to cached city insights from service23 data analyst agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Pydantic Models
# ============================================================================

class ChatQueryRequest(BaseModel):
    """Request model for natural language queries"""
    query: str = Field(..., description="Natural language query about a city or country")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Show me the insights for Bristol"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat queries"""
    reply: str = Field(..., description="One line summary of the insight")
    replySummary: str = Field(..., description="One paragraph summary of the insight")
    table: str = Field(default="service23_data_analyst_insights", description="Database table name")
    id: str = Field(..., description="UUID of the insight record")


class InsightDetail(BaseModel):
    """Detailed insight record"""
    id: str
    city: str
    country_code: str
    success_criteria: Optional[str] = None
    insight_summary: str
    detailed_analysis: str
    data_sources_used: Optional[List[str]] = []
    confidence_score: Optional[float] = None
    recommendations: Optional[List[Dict]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    alert_sent: Optional[bool] = False
    alert_id: Optional[str] = None


class InsightSummary(BaseModel):
    """Summary view of insight"""
    id: str
    city: str
    country_code: str
    insight_summary: str
    confidence_score: Optional[float] = None
    created_at: Optional[datetime] = None


# ============================================================================
# Database Operations
# ============================================================================

def get_db_connection():
    """Create PostgreSQL connection"""
    return psycopg2.connect(**DB_CONFIG)


def get_latest_insight(city_name: Optional[str] = None, country_code: Optional[str] = None) -> Optional[Dict]:
    """Get the most recent insight"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        if city_name and country_code:
            cursor.execute("""
                SELECT * FROM service23_data_analyst_insights
                WHERE LOWER(city) = LOWER(%s) AND LOWER(country_code) = LOWER(%s)
                ORDER BY created_at DESC
                LIMIT 1
            """, (city_name, country_code))
        elif city_name:
            cursor.execute("""
                SELECT * FROM service23_data_analyst_insights
                WHERE LOWER(city) = LOWER(%s)
                ORDER BY created_at DESC
                LIMIT 1
            """, (city_name,))
        else:
            cursor.execute("""
                SELECT * FROM service23_data_analyst_insights
                ORDER BY created_at DESC
                LIMIT 1
            """)

        insight = cursor.fetchone()
        cursor.close()
        conn.close()

        return dict(insight) if insight else None
    except Exception as e:
        print(f"[ERROR] Database query failed: {e}")
        return None


def get_insights_by_country(country_code: str, limit: int = 100) -> List[Dict]:
    """Get latest insights for all cities in a country (for investors)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT * FROM service23_data_analyst_insights
            WHERE LOWER(country_code) = LOWER(%s)
            ORDER BY created_at DESC
            LIMIT %s
        """, (country_code, limit))

        insights = cursor.fetchall()
        cursor.close()
        conn.close()

        return [dict(insight) for insight in insights]
    except Exception as e:
        print(f"[ERROR] Database query failed: {e}")
        return []


def get_city_insight(city_name: str, country_code: str) -> Optional[Dict]:
    """Get latest insight for a specific city and country (for council officials)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT * FROM service23_data_analyst_insights
            WHERE LOWER(city) = LOWER(%s) AND LOWER(country_code) = LOWER(%s)
            ORDER BY created_at DESC
            LIMIT 1
        """, (city_name, country_code))

        insight = cursor.fetchone()
        cursor.close()
        conn.close()

        return dict(insight) if insight else None
    except Exception as e:
        print(f"[ERROR] Database query failed: {e}")
        return None


def get_recent_insights(limit: int = 10) -> List[Dict]:
    """Get recent insights across all cities"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                id,
                city,
                country_code,
                insight_summary,
                confidence_score,
                created_at
            FROM service23_data_analyst_insights
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))

        insights = cursor.fetchall()
        cursor.close()
        conn.close()

        return [dict(insight) for insight in insights]
    except Exception as e:
        print(f"[ERROR] Database query failed: {e}")
        return []


def parse_query_for_location(query: str) -> tuple[Optional[str], Optional[str]]:
    """
    Simple parser to extract city and country from natural language query.
    For now, uses basic string matching. Can be enhanced with NLP later.

    Returns: (city_name, country_code)
    """
    query_lower = query.lower()

    # Common city names to look for
    cities = ["bristol", "manchester", "birmingham", "leeds", "edinburgh",
              "london", "boston", "dubai", "singapore", "tokyo", "glasgow",
              "liverpool", "newcastle", "sheffield", "nottingham"]

    # Country code mapping
    country_keywords = {
        "GB": ["uk", "britain", "england", "scotland", "wales", "united kingdom"],
        "US": ["usa", "america", "united states"],
        "AE": ["uae", "dubai", "emirates"],
        "SG": ["singapore"],
        "JP": ["japan"]
    }

    # Find city
    city_name = None
    for city in cities:
        if city in query_lower:
            city_name = city.capitalize()
            break

    # Find country code (default to GB)
    country_code = "GB"
    for code, keywords in country_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            country_code = code
            break

    return city_name, country_code


def generate_insight_summary(insight: Dict) -> tuple[str, str]:
    """
    Generate one-line and one-paragraph summaries of the insight.

    Returns: (one_line_summary, paragraph_summary)
    """
    city = insight.get('city', 'Unknown')
    confidence = insight.get('confidence_score')
    created_at = insight.get('created_at', 'Unknown date')

    # Format created_at if it's a datetime object
    if isinstance(created_at, datetime):
        created_at = created_at.strftime('%Y-%m-%d %H:%M')

    # One-line summary (use existing insight_summary)
    one_line = insight.get('insight_summary', f"{city} city insights analysis")

    # Paragraph summary (use first part of detailed_analysis)
    detailed = insight.get('detailed_analysis', '')

    # Build confidence indicator
    confidence_text = ""
    if confidence is not None:
        confidence_pct = int(confidence * 100)
        confidence_text = f" (Confidence: {confidence_pct}%)"

    # Extract first paragraph or first 300 chars of detailed analysis
    if detailed:
        paragraphs = detailed.split('\n\n')
        first_para = paragraphs[0] if paragraphs else detailed[:300]

        paragraph = (
            f"Analysis for {city} generated on {created_at}{confidence_text}. "
            f"{first_para[:400]}..."
        )
    else:
        paragraph = (
            f"City insights for {city} generated on {created_at}{confidence_text}. "
            f"Full analysis available in database."
        )

    # Add recommendations summary if available
    recommendations = insight.get('recommendations', [])
    if isinstance(recommendations, list) and recommendations:
        paragraph += f" Generated {len(recommendations)} actionable recommendations."

    return one_line, paragraph


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "service": "City Insights Microservice",
        "status": "running",
        "version": "1.0.0",
        "port": os.getenv("PORT", 8024),
        "docs": "/docs",
        "table": "service23_data_analyst_insights"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check with database connectivity"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM service23_data_analyst_insights")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        return {
            "status": "healthy",
            "service": "city_insights_microservice",
            "database": "connected",
            "insights_count": count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "city_insights_microservice",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.post("/chat/city", response_model=ChatResponse, tags=["Chat"])
async def get_city_insight_endpoint(request: ChatQueryRequest):
    """
    Natural language query for specific city insights (for council officials)

    Accepts natural language queries like:
    - "Show me the insights for Bristol"
    - "What insights do we have for Manchester?"
    - "Tell me about Edinburgh's data analysis"

    Returns latest insight for the specified city with summary.

    **Use case:** Council officials checking their city's insights
    """
    # Parse query to extract city and country
    city_name, country_code = parse_query_for_location(request.query)

    if not city_name:
        raise HTTPException(
            status_code=400,
            detail="Could not identify a city in your query. Please mention a specific city name."
        )

    # Get latest insight for the city
    insight = get_city_insight(city_name, country_code)

    if not insight:
        raise HTTPException(
            status_code=404,
            detail=f"No insights found for {city_name}, {country_code}"
        )

    # Generate summaries
    one_line, paragraph = generate_insight_summary(insight)

    return ChatResponse(
        reply=one_line,
        replySummary=paragraph,
        table="service23_data_analyst_insights",
        id=str(insight['id'])
    )


@app.post("/chat/cities", response_model=ChatResponse, tags=["Chat"])
async def get_cities_insights(request: ChatQueryRequest):
    """
    Natural language query for city insights by country (for investors)

    Accepts natural language queries like:
    - "Show me cities in the UK"
    - "What cities are available in Great Britain?"
    - "List all UK city insights"

    Returns latest insight for the specified country with summary.

    **Use case:** Investors exploring investment opportunities
    """
    # Parse query to extract location
    city_name, country_code = parse_query_for_location(request.query)

    # For cities endpoint, we look for country-level queries
    # If no specific city mentioned, return latest insight for that country
    insights = get_insights_by_country(country_code)

    if not insights:
        raise HTTPException(
            status_code=404,
            detail=f"No insights found for country: {country_code}"
        )

    # Return the most recent insight for the country
    latest_insight = insights[0]
    one_line, paragraph = generate_insight_summary(latest_insight)

    return ChatResponse(
        reply=one_line,
        replySummary=paragraph,
        table="service23_data_analyst_insights",
        id=str(latest_insight['id'])
    )


@app.get("/insights/recent", response_model=List[InsightSummary], tags=["Insights"])
async def get_recent_insights_endpoint(limit: int = 10):
    """
    Get recent insights across all cities

    Returns a list of recent insights with summary information.
    Useful for dashboards and overview pages.
    """
    insights = get_recent_insights(limit)

    return [
        InsightSummary(
            id=str(insight['id']),
            city=insight['city'],
            country_code=insight['country_code'],
            insight_summary=insight['insight_summary'],
            confidence_score=insight.get('confidence_score'),
            created_at=insight.get('created_at')
        )
        for insight in insights
    ]


@app.get("/insights/{insight_id}", response_model=InsightDetail, tags=["Insights"])
async def get_insight_by_id(insight_id: str):
    """
    Get a specific insight by its UUID

    Returns complete insight details including recommendations and data sources.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT * FROM service23_data_analyst_insights
            WHERE id = %s
        """, (insight_id,))

        insight = cursor.fetchone()
        cursor.close()
        conn.close()

        if not insight:
            raise HTTPException(
                status_code=404,
                detail=f"Insight with ID {insight_id} not found"
            )

        return InsightDetail(
            id=str(insight['id']),
            city=insight['city'],
            country_code=insight['country_code'],
            success_criteria=insight.get('success_criteria'),
            insight_summary=insight['insight_summary'],
            detailed_analysis=insight['detailed_analysis'],
            data_sources_used=insight.get('data_sources_used', []),
            confidence_score=insight.get('confidence_score'),
            recommendations=insight.get('recommendations', []),
            created_at=insight.get('created_at'),
            updated_at=insight.get('updated_at'),
            alert_sent=insight.get('alert_sent', False),
            alert_id=insight.get('alert_id')
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )


@app.get("/insights/city/{city_name}", response_model=List[InsightSummary], tags=["Insights"])
async def get_insights_for_city(city_name: str, country_code: str = "GB", limit: int = 10):
    """
    Get all insights for a specific city

    Returns historical insights for the specified city.
    Useful for tracking changes over time.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                id,
                city,
                country_code,
                insight_summary,
                confidence_score,
                created_at
            FROM service23_data_analyst_insights
            WHERE LOWER(city) = LOWER(%s) AND LOWER(country_code) = LOWER(%s)
            ORDER BY created_at DESC
            LIMIT %s
        """, (city_name, country_code, limit))

        insights = cursor.fetchall()
        cursor.close()
        conn.close()

        if not insights:
            raise HTTPException(
                status_code=404,
                detail=f"No insights found for {city_name}, {country_code}"
            )

        return [
            InsightSummary(
                id=str(insight['id']),
                city=insight['city'],
                country_code=insight['country_code'],
                insight_summary=insight['insight_summary'],
                confidence_score=insight.get('confidence_score'),
                created_at=insight.get('created_at')
            )
            for insight in insights
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )


# ============================================================================
# Startup Event
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    print("="*60)
    print("CITY INSIGHTS MICROSERVICE STARTING")
    print("="*60)
    port = os.getenv("PORT", 8024)
    print(f"API Documentation: http://localhost:{port}/docs")
    print(f"Alternative Docs: http://localhost:{port}/redoc")
    print("="*60)

    # Test database connection
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM service23_data_analyst_insights")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"[OK] PostgreSQL connection successful")
        print(f"[OK] Found {count} insights in database")
    except Exception as e:
        print(f"[ERROR] PostgreSQL connection failed: {e}")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8024))

    uvicorn.run(
        "insights_microservice:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
