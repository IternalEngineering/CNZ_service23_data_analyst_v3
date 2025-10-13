# Data Analyst Agent Implementation Plan
## Claude SDK Integration with Production EC2 & PostgreSQL

---

## Executive Summary

This plan outlines the implementation of a Data Analyst Agent using the Claude SDK (Anthropic Python SDK) to run on our production EC2 instance with direct access to our PostgreSQL database (AWS RDS). The agent will leverage the RAG API endpoints and database connections to perform automated research, data analysis, and report generation.

---

## 1. Current Infrastructure Review

### Production Environment
- **EC2 Instance**: t3.medium (35.179.135.187)
- **Region**: eu-west-2 (London)
- **Database**: AWS RDS PostgreSQL 16.3
  - Endpoint: `urbanzero-db.c5qeo4ayy5u5.eu-west-2.rds.amazonaws.com`
  - SSL Required: `sslmode=require`
  - ORM: Drizzle ORM (TypeScript), asyncpg (Python)

### Existing Infrastructure
- **Data Warehouse**: Snowflake (analytics, large-scale processing)
- **Storage**: AWS S3 + Google Cloud Storage
- **Message Queue**: SQS for async processing
- **API Framework**: FastAPI (Python services), Express.js (Node backend)
- **AI Services**: CrewAI agents, OpenAI GPT-4o
- **Monitoring**: Arize Phoenix for AI telemetry

### Available Services
- **RAG API Servers**:
  - Production: `cnz-rag.icmserver007.com`
  - CL Server: `cnz-cl.icmserver007.com`
  - Local: `localhost:8000` (main), `localhost:8001` (standalone)

### Database Access Pattern
```python
# Current pattern using asyncpg
import asyncpg

DATABASE_URL = os.getenv('DATABASE_URL')
conn = await asyncpg.connect(DATABASE_URL, ssl='require')
```

---

## 2. Agent Architecture Design

### 2.1 Technology Stack

#### Core Components
```python
# Primary SDK
anthropic>=0.48.0          # Claude Python SDK

# Database & Data
asyncpg>=0.29.0            # PostgreSQL async connector
psycopg2-binary>=2.9.9     # PostgreSQL sync connector (backup)
sqlalchemy>=2.0.0          # ORM for complex queries
snowflake-connector-python # Snowflake integration

# API & Web
fastapi>=0.115.0           # API framework
uvicorn>=0.32.0            # ASGI server
httpx>=0.27.0              # Async HTTP client
requests>=2.32.0           # Sync HTTP client

# AI & ML
openai>=1.58.1             # OpenAI SDK (existing workflows)
litellm>=1.52.0            # Multi-LLM abstraction
langchain>=0.3.0           # Tool ecosystem

# Monitoring & Logging
arize>=7.28.0              # AI observability
python-decouple>=3.8       # Environment config
structlog>=24.4.0          # Structured logging
```

### 2.2 Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Analyst Agent                        │
│                  (Claude SDK + Tools)                        │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Database   │   │   RAG API    │   │  Snowflake   │
│     Tool     │   │     Tool     │   │     Tool     │
└──────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  PostgreSQL  │   │  ChromaDB    │   │  Snowflake   │
│     RDS      │   │  RAG Index   │   │  Warehouse   │
└──────────────┘   └──────────────┘   └──────────────┘
```

### 2.3 Agent Capabilities

#### Primary Functions
1. **Data Analysis**
   - Query PostgreSQL for transactional data
   - Query Snowflake for analytics and time-series
   - Perform statistical analysis and pattern recognition
   - Generate data quality reports

2. **Research & RAG**
   - Query academic papers via RAG API
   - Extract city statistics from indexed documents
   - Cross-reference multiple data sources
   - Build knowledge graphs from findings

3. **Report Generation**
   - Create comprehensive analytical reports
   - Generate visualizations and charts
   - Export findings to multiple formats (PDF, CSV, JSON)
   - Schedule automated reporting

4. **Data Integration**
   - Sync data between PostgreSQL and Snowflake
   - Monitor data quality and consistency
   - Trigger ETL workflows
   - Validate data integrity

---

## 3. Database Integration & Security

### 3.1 Connection Management

#### Environment Variables (`.env`)
```bash
# Claude SDK
ANTHROPIC_API_KEY=sk-ant-xxx...

# PostgreSQL RDS
DATABASE_URL=postgresql://user:password@urbanzero-db.c5qeo4ayy5u5.eu-west-2.rds.amazonaws.com:5432/urbanzero?sslmode=require
POSTGRES_HOST=urbanzero-db.c5qeo4ayy5u5.eu-west-2.rds.amazonaws.com
POSTGRES_PORT=5432
POSTGRES_DB=urbanzero
POSTGRES_USER=urbanzero_user
POSTGRES_PASSWORD=xxx...
POSTGRES_SSL_MODE=require

# Snowflake
SNOWFLAKE_ACCOUNT=PVYTWHR-LR82658
SNOWFLAKE_USER=MAIN_SERVICE_ACCOUNT_CNZ
SNOWFLAKE_PASSWORD=xxx...
SNOWFLAKE_DATABASE=SNOWFLAKE_LEARNING_WH
SNOWFLAKE_SCHEMA=CURATED
SNOWFLAKE_WAREHOUSE=SNOWFLAKE_LEARNING_WH
SNOWFLAKE_ROLE=ACCOUNTADMIN

# RAG API
RAG_API_URL=http://cnz-rag.icmserver007.com
RAG_API_TIMEOUT=30

# Service Configuration
AGENT_PORT=8012
AGENT_HOST=0.0.0.0
LOG_LEVEL=INFO
```

#### Database Tool Implementation
```python
# database_tool.py
import asyncpg
import os
from typing import Dict, List, Any

class DatabaseTool:
    """PostgreSQL database tool for Claude SDK agent"""

    def __init__(self):
        self.connection_string = os.getenv('DATABASE_URL')
        self.pool = None

    async def initialize(self):
        """Initialize connection pool"""
        self.pool = await asyncpg.create_pool(
            self.connection_string,
            ssl='require',
            min_size=2,
            max_size=10,
            command_timeout=60
        )

    async def query(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute SELECT query"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql, *(params or ()))
            return [dict(row) for row in rows]

    async def execute(self, sql: str, params: tuple = None) -> str:
        """Execute INSERT/UPDATE/DELETE"""
        async with self.pool.acquire() as conn:
            result = await conn.execute(sql, *(params or ()))
            return result

    async def get_schema(self, table_name: str = None) -> Dict[str, Any]:
        """Get table schema information"""
        if table_name:
            sql = """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = $1
                ORDER BY ordinal_position
            """
            return await self.query(sql, (table_name,))
        else:
            sql = """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
            return await self.query(sql)

    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
```

### 3.2 Security Measures

#### Access Control
1. **Database User Permissions**
   - Create dedicated read-only user for agent queries
   - Use separate write-enabled user for data modifications
   - Implement row-level security where applicable

```sql
-- Create read-only user for agent
CREATE USER data_analyst_agent WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE urbanzero TO data_analyst_agent;
GRANT USAGE ON SCHEMA public TO data_analyst_agent;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO data_analyst_agent;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO data_analyst_agent;

-- Create write user for data operations (limited)
CREATE USER data_analyst_writer WITH PASSWORD 'secure_password';
GRANT INSERT, UPDATE ON specific_tables TO data_analyst_writer;
```

#### Network Security
1. **EC2 Security Group Rules**
   - Allow inbound on agent port (8012) from trusted IPs only
   - Allow outbound to RDS on port 5432
   - Allow outbound to RAG API servers
   - Allow outbound HTTPS for Claude API

2. **RDS Security Group**
   - Allow inbound from EC2 instance security group
   - Require SSL/TLS connections
   - Enable encryption at rest

#### API Key Management
1. **Environment Variables**
   - Store all API keys in `.env` file (never commit)
   - Use AWS Secrets Manager for production (planned)
   - Rotate keys quarterly

2. **Claude API Key Protection**
   - Use separate API key for production vs development
   - Monitor usage and set billing alerts
   - Implement rate limiting

---

## 4. Agent Tools & Capabilities

### 4.1 Core Tools

#### Tool 1: Database Query Tool
```python
# tools/database_query_tool.py
from anthropic import types

database_query_tool = types.ToolParam(
    name="query_database",
    description="Execute SQL queries against PostgreSQL database. Use for transactional data, user info, opportunities, reports, and data sources.",
    input_schema={
        "type": "object",
        "properties": {
            "sql": {
                "type": "string",
                "description": "SQL query to execute (SELECT only for safety)"
            },
            "parameters": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Query parameters for parameterized queries"
            }
        },
        "required": ["sql"]
    }
)

async def execute_database_query(sql: str, parameters: list = None):
    """Execute database query with safety checks"""
    # Validate SQL (only SELECT allowed for safety)
    if not sql.strip().upper().startswith('SELECT'):
        return {"error": "Only SELECT queries allowed"}

    try:
        db_tool = DatabaseTool()
        await db_tool.initialize()
        results = await db_tool.query(sql, tuple(parameters or []))
        await db_tool.close()
        return {"success": True, "data": results, "row_count": len(results)}
    except Exception as e:
        return {"error": str(e)}
```

#### Tool 2: RAG Query Tool
```python
# tools/rag_query_tool.py
import httpx
from anthropic import types

rag_query_tool = types.ToolParam(
    name="query_rag_pdfs",
    description="Search academic papers and city documents using RAG (Retrieval-Augmented Generation). Use for research questions, finding papers, extracting city statistics.",
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Research question or search query"
            },
            "mode": {
                "type": "string",
                "enum": ["hybrid", "semantic", "keyword"],
                "description": "Search mode: hybrid (best), semantic (contextual), keyword (exact)"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return (default: 10)"
            }
        },
        "required": ["query"]
    }
)

async def execute_rag_query(query: str, mode: str = "hybrid", limit: int = 10):
    """Query RAG API for document search"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{os.getenv('RAG_API_URL')}/api/query-pdfs",
                json={"query": query, "mode": mode, "limit": limit}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": str(e)}
```

#### Tool 3: Snowflake Analytics Tool
```python
# tools/snowflake_query_tool.py
import snowflake.connector
from anthropic import types

snowflake_query_tool = types.ToolParam(
    name="query_snowflake",
    description="Query Snowflake data warehouse for analytics, time-series data, and large-scale processing. Use for historical trends, aggregations, and complex analytics.",
    input_schema={
        "type": "object",
        "properties": {
            "sql": {
                "type": "string",
                "description": "SQL query to execute against Snowflake"
            },
            "warehouse": {
                "type": "string",
                "description": "Snowflake warehouse to use (default: SNOWFLAKE_LEARNING_WH)"
            }
        },
        "required": ["sql"]
    }
)

async def execute_snowflake_query(sql: str, warehouse: str = None):
    """Execute Snowflake query"""
    try:
        conn = snowflake.connector.connect(
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA'),
            warehouse=warehouse or os.getenv('SNOWFLAKE_WAREHOUSE'),
            role=os.getenv('SNOWFLAKE_ROLE')
        )
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        return {
            "success": True,
            "data": [dict(zip(columns, row)) for row in results],
            "row_count": len(results)
        }
    except Exception as e:
        return {"error": str(e)}
```

#### Tool 4: Report Generation Tool
```python
# tools/report_generator_tool.py
from anthropic import types

report_generator_tool = types.ToolParam(
    name="generate_report",
    description="Generate formatted reports (PDF, CSV, JSON) from analysis results. Supports charts, tables, and visualizations.",
    input_schema={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Report title"
            },
            "content": {
                "type": "string",
                "description": "Report content in markdown format"
            },
            "format": {
                "type": "string",
                "enum": ["pdf", "csv", "json", "markdown"],
                "description": "Output format"
            },
            "data": {
                "type": "object",
                "description": "Structured data to include in report"
            }
        },
        "required": ["title", "content", "format"]
    }
)

async def generate_report(title: str, content: str, format: str, data: dict = None):
    """Generate and save report"""
    import os
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{timestamp}.{format}"
    filepath = os.path.join("reports", filename)

    # Create reports directory if it doesn't exist
    os.makedirs("reports", exist_ok=True)

    if format == "markdown":
        with open(filepath, 'w') as f:
            f.write(f"# {title}\n\n{content}")
    elif format == "json":
        import json
        with open(filepath, 'w') as f:
            json.dump({"title": title, "content": content, "data": data}, f, indent=2)
    # ... other formats

    return {"success": True, "filepath": filepath}
```

### 4.2 Tool Execution Pattern

```python
# agent.py
import anthropic
from typing import List
import os

class DataAnalystAgent:
    """Claude SDK-powered Data Analyst Agent"""

    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        self.model = "claude-sonnet-4-5-20250929"
        self.tools = [
            database_query_tool,
            rag_query_tool,
            snowflake_query_tool,
            report_generator_tool
        ]
        self.tool_handlers = {
            "query_database": execute_database_query,
            "query_rag_pdfs": execute_rag_query,
            "query_snowflake": execute_snowflake_query,
            "generate_report": generate_report
        }

    async def process_tool_call(self, tool_name: str, tool_input: dict):
        """Execute tool and return result"""
        handler = self.tool_handlers.get(tool_name)
        if not handler:
            return {"error": f"Unknown tool: {tool_name}"}

        return await handler(**tool_input)

    async def run(self, user_message: str, context: List[dict] = None):
        """Run agent with message and context"""
        messages = context or []
        messages.append({
            "role": "user",
            "content": user_message
        })

        while True:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                tools=self.tools,
                messages=messages
            )

            # Check for tool use
            if response.stop_reason == "tool_use":
                # Execute all tool calls
                tool_results = []
                for content in response.content:
                    if content.type == "tool_use":
                        result = await self.process_tool_call(
                            content.name,
                            content.input
                        )
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": str(result)
                        })

                # Add assistant response and tool results to messages
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
            else:
                # Final response
                return response.content[0].text
```

---

## 5. Deployment Strategy for EC2

### 5.1 Directory Structure

```
/opt/urbanzero/data_analyst_agent/
├── agent.py                  # Main agent class
├── main.py                   # FastAPI server
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not committed)
├── tools/
│   ├── __init__.py
│   ├── database_tool.py
│   ├── rag_tool.py
│   ├── snowflake_tool.py
│   └── report_tool.py
├── utils/
│   ├── __init__.py
│   ├── logging.py
│   └── monitoring.py
├── reports/                  # Generated reports
├── logs/                     # Application logs
├── tests/                    # Unit and integration tests
└── docs/                     # Documentation
    ├── RAG_API_ENDPOINTS.md
    └── IMPLEMENTATION_PLAN.md
```

### 5.2 FastAPI Server

```python
# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os

from agent import DataAnalystAgent

app = FastAPI(
    title="Data Analyst Agent API",
    description="Claude SDK-powered data analysis agent",
    version="1.0.0"
)

agent = DataAnalystAgent()

class AnalysisRequest(BaseModel):
    query: str
    context: Optional[List[dict]] = None

class AnalysisResponse(BaseModel):
    result: str
    success: bool
    error: Optional[str] = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "data_analyst_agent"}

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):
    """
    Run data analysis using Claude SDK agent

    Examples:
    - "What is the average ROI for opportunities in London?"
    - "Find recent academic papers on Net Zero strategies"
    - "Generate a report on solar panel adoption trends"
    """
    try:
        result = await agent.run(request.query, request.context)
        return AnalysisResponse(result=result, success=True)
    except Exception as e:
        return AnalysisResponse(result="", success=False, error=str(e))

@app.get("/api/tools")
async def list_tools():
    """List available tools"""
    return {
        "tools": [
            {
                "name": tool["name"],
                "description": tool["description"]
            }
            for tool in agent.tools
        ]
    }

if __name__ == "__main__":
    port = int(os.getenv("AGENT_PORT", 8012))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### 5.3 Systemd Service

```ini
# /etc/systemd/system/data-analyst-agent.service
[Unit]
Description=Data Analyst Agent (Claude SDK)
After=network.target postgresql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/urbanzero/data_analyst_agent
Environment="PATH=/opt/urbanzero/data_analyst_agent/venv/bin"
ExecStart=/opt/urbanzero/data_analyst_agent/venv/bin/python main.py
Restart=always
RestartSec=10

# Logging
StandardOutput=append:/opt/urbanzero/data_analyst_agent/logs/agent.log
StandardError=append:/opt/urbanzero/data_analyst_agent/logs/agent_error.log

[Install]
WantedBy=multi-user.target
```

### 5.4 Deployment Script

```bash
#!/bin/bash
# deploy.sh

set -e

echo "Deploying Data Analyst Agent to EC2..."

# Configuration
DEPLOY_DIR="/opt/urbanzero/data_analyst_agent"
EC2_HOST="35.179.135.187"
EC2_USER="ubuntu"
SERVICE_NAME="data-analyst-agent"

# Create deployment package
echo "Creating deployment package..."
tar -czf data_analyst_agent.tar.gz \
    agent.py \
    main.py \
    requirements.txt \
    tools/ \
    utils/ \
    .env

# Copy to EC2
echo "Copying to EC2..."
scp data_analyst_agent.tar.gz ${EC2_USER}@${EC2_HOST}:/tmp/

# Deploy on EC2
echo "Deploying on EC2..."
ssh ${EC2_USER}@${EC2_HOST} << 'ENDSSH'
    set -e

    # Create directory
    sudo mkdir -p /opt/urbanzero/data_analyst_agent
    sudo chown ubuntu:ubuntu /opt/urbanzero/data_analyst_agent

    # Extract
    cd /opt/urbanzero/data_analyst_agent
    tar -xzf /tmp/data_analyst_agent.tar.gz

    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate

    # Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt

    # Create directories
    mkdir -p reports logs tests

    # Install systemd service
    sudo cp /opt/urbanzero/data_analyst_agent/data-analyst-agent.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable data-analyst-agent
    sudo systemctl restart data-analyst-agent

    # Check status
    sudo systemctl status data-analyst-agent
ENDSSH

echo "Deployment complete!"
echo "Service running on http://${EC2_HOST}:8012"
```

### 5.5 Nginx Configuration

```nginx
# /etc/nginx/sites-available/data-analyst-agent
server {
    listen 80;
    server_name data-analyst.urbanzero.com;

    location / {
        proxy_pass http://localhost:8012;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

---

## 6. Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [x] Document infrastructure review
- [ ] Set up development environment locally
- [ ] Install Claude SDK and dependencies
- [ ] Create basic agent structure
- [ ] Implement database tool with connection pooling
- [ ] Test PostgreSQL connectivity

### Phase 2: Core Tools (Week 2)
- [ ] Implement RAG query tool
- [ ] Implement Snowflake query tool
- [ ] Implement report generation tool
- [ ] Write unit tests for each tool
- [ ] Test tool integration with Claude SDK
- [ ] Add error handling and logging

### Phase 3: Agent Logic (Week 3)
- [ ] Build agent orchestration logic
- [ ] Implement tool execution flow
- [ ] Add conversation context management
- [ ] Create agent prompts and system messages
- [ ] Test multi-tool workflows
- [ ] Implement streaming responses (optional)

### Phase 4: API Layer (Week 4)
- [ ] Build FastAPI server
- [ ] Create API endpoints
- [ ] Add request validation
- [ ] Implement authentication (API keys)
- [ ] Add rate limiting
- [ ] Write API documentation

### Phase 5: Security & Monitoring (Week 5)
- [ ] Implement database access controls
- [ ] Set up SSL/TLS for connections
- [ ] Configure Arize monitoring
- [ ] Add structured logging
- [ ] Implement error tracking
- [ ] Security audit

### Phase 6: Deployment (Week 6)
- [ ] Create deployment scripts
- [ ] Set up systemd service
- [ ] Configure Nginx reverse proxy
- [ ] Deploy to EC2 staging environment
- [ ] Run integration tests
- [ ] Performance testing and optimization

### Phase 7: Production Launch (Week 7)
- [ ] Production deployment
- [ ] Monitoring dashboard setup
- [ ] Documentation finalization
- [ ] Team training
- [ ] Go-live checklist
- [ ] Post-launch monitoring

---

## 7. Testing Strategy

### Unit Tests
```python
# tests/test_database_tool.py
import pytest
from tools.database_tool import DatabaseTool

@pytest.mark.asyncio
async def test_database_connection():
    """Test database connection"""
    tool = DatabaseTool()
    await tool.initialize()
    result = await tool.query("SELECT 1 as test")
    assert result[0]['test'] == 1
    await tool.close()

@pytest.mark.asyncio
async def test_get_schema():
    """Test schema retrieval"""
    tool = DatabaseTool()
    await tool.initialize()
    tables = await tool.get_schema()
    assert len(tables) > 0
    await tool.close()
```

### Integration Tests
```python
# tests/test_agent_integration.py
import pytest
from agent import DataAnalystAgent

@pytest.mark.asyncio
async def test_database_query_flow():
    """Test full agent workflow with database query"""
    agent = DataAnalystAgent()
    result = await agent.run(
        "How many opportunities are in the database?"
    )
    assert "opportunities" in result.lower()

@pytest.mark.asyncio
async def test_rag_query_flow():
    """Test RAG query workflow"""
    agent = DataAnalystAgent()
    result = await agent.run(
        "Find papers about Net Zero carbon reduction"
    )
    assert result is not None
```

---

## 8. Monitoring & Observability

### Metrics to Track
1. **Performance**
   - Request latency (p50, p95, p99)
   - Tool execution time
   - Database query performance
   - RAG API response time

2. **Usage**
   - Requests per minute/hour/day
   - Most used tools
   - Common query patterns
   - Error rates

3. **AI Metrics (Arize)**
   - Token usage per request
   - Model latency
   - Tool call frequency
   - Conversation length

### Logging Structure
```python
# utils/logging.py
import structlog
import logging

def setup_logging():
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True
    )

    return structlog.get_logger()

# Usage
logger = setup_logging()
logger.info("agent_request", query="...", user_id="...", tools_used=[...])
```

---

## 9. Cost Estimation

### Claude API Costs
- **Model**: Claude Sonnet 4.5
- **Input**: ~$3 per million tokens
- **Output**: ~$15 per million tokens
- **Estimated**: ~$100-300/month for moderate usage

### Infrastructure Costs
- **EC2**: Already running (no additional cost)
- **RDS**: Already running (no additional cost)
- **Snowflake**: Pay-per-query (existing)
- **Total Additional**: ~$100-300/month (primarily Claude API)

---

## 10. Success Criteria

### Technical Metrics
- [ ] Agent responds within 5 seconds for simple queries
- [ ] Database queries execute within 2 seconds
- [ ] RAG queries return within 10 seconds
- [ ] 99% uptime SLA
- [ ] Error rate < 1%

### Functional Metrics
- [ ] Successfully query PostgreSQL database
- [ ] Successfully query RAG API
- [ ] Successfully query Snowflake
- [ ] Generate formatted reports
- [ ] Handle multi-step analysis workflows
- [ ] Maintain conversation context

### Business Metrics
- [ ] Reduce manual data analysis time by 70%
- [ ] Generate 10+ automated reports per week
- [ ] Enable self-service analytics for team
- [ ] Improve data-driven decision making

---

## 11. Risk Mitigation

### Technical Risks
| Risk | Impact | Mitigation |
|------|--------|-----------|
| API rate limits | High | Implement request queuing and caching |
| Database overload | High | Connection pooling, read replicas |
| Claude API costs | Medium | Token usage monitoring, response caching |
| Network latency | Medium | Deploy close to data sources, use async |
| Tool execution errors | Medium | Comprehensive error handling, retries |

### Security Risks
| Risk | Impact | Mitigation |
|------|--------|-----------|
| SQL injection | Critical | Parameterized queries only |
| API key exposure | Critical | Environment variables, AWS Secrets Manager |
| Unauthorized access | High | API authentication, IP whitelisting |
| Data leakage | High | Audit logs, access controls |

---

## 12. Next Steps

1. **Immediate Actions**
   - [ ] Create project directory structure
   - [ ] Set up virtual environment
   - [ ] Install Claude SDK and dependencies
   - [ ] Create `.env` file with credentials
   - [ ] Test basic Claude SDK connection

2. **Week 1 Deliverables**
   - [ ] Working database tool
   - [ ] Basic agent structure
   - [ ] Local development environment
   - [ ] Unit tests for database tool

3. **Documentation**
   - [ ] API documentation (Swagger)
   - [ ] Tool usage guide
   - [ ] Deployment runbook
   - [ ] Troubleshooting guide

---

## 13. References

- **Claude SDK Documentation**: https://docs.claude.com/en/api/agent-sdk/overview
- **Anthropic Python SDK**: https://github.com/anthropics/anthropic-sdk-python
- **PostgreSQL asyncpg**: https://magicstack.github.io/asyncpg/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Snowflake Python Connector**: https://docs.snowflake.com/en/user-guide/python-connector

---

**Last Updated**: 2025-10-03
**Version**: 1.0
**Author**: Claude Code (UrbanZero Team)
