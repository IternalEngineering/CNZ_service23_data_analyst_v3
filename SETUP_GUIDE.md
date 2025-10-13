# Service23 MindsDB Setup Guide

This guide provides step-by-step instructions for setting up and using MindsDB with Service23 (Data Analyst Agent).

## Overview

Service23 is a data analyst agent that connects to the UrbanZero PostgreSQL database via MindsDB. MindsDB runs on an EC2 instance and is accessed through an SSH tunnel.

### Architecture

```
[Service23] → [SSH Tunnel] → [EC2 MindsDB] → [RDS PostgreSQL]
   Local         Port 47334      18.168.195.169   urbanzero-db
```

## Prerequisites

1. **SSH Key**: `C:\Users\chriz\.ssh\cnz-staging-key.pem` (must exist)
2. **Python**: Python 3.11+ installed
3. **Network**: Access to EC2 instance 18.168.195.169
4. **Dependencies**: Install Python dependencies (see below)

## Quick Start

### Step 1: Install Dependencies

```bash
# Navigate to service23 directory
cd C:\Users\chriz\OneDrive\Documents\CNZ\UrbanZero2\UrbanZero\server_c\service23

# Create virtual environment (if not exists)
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat

# Install required packages
pip install requests
```

### Step 2: Start SSH Tunnel

**Option A - PowerShell (Recommended)**
```powershell
.\setup_tunnel.ps1
```

**Option B - Batch Script**
```batch
start_tunnel.bat
```

**Option C - Manual SSH Command**
```bash
ssh -i C:\Users\chriz\.ssh\cnz-staging-key.pem -N -L 47334:localhost:47334 ec2-user@18.168.195.169
```

**Expected Output:**
```
Setting up SSH tunnel to MindsDB...
EC2 Host: 18.168.195.169
Local Port: 47334
Remote Port: 47334

Starting SSH tunnel (press Ctrl+C to stop)...
Once connected, MindsDB will be available at http://localhost:47334
```

**Leave this terminal open** - the tunnel must remain running for MindsDB access.

### Step 3: Verify Connection

In a **new terminal**, verify MindsDB is accessible:

```bash
# Check MindsDB status
curl http://localhost:47334/api/status
```

**Expected Response:**
```json
{
  "mindsdb_version": "25.5.4.0",
  "environment": "local",
  "auth": {"http_auth_enabled": false}
}
```

### Step 4: Run Test Suite

```bash
# Run comprehensive test suite
python test_mindsdb_connection.py
```

**Expected Output:**
```
============================================================
  MindsDB Connection Test Suite
  Service23 - Data Analyst Agent
============================================================

============================================================
  Testing MindsDB Connection
============================================================
Checking MindsDB status...
✅ SUCCESS: Connected to MindsDB
   Version: 25.5.4.0
   Environment: local
   Auth: {'http_auth_enabled': False}

... [additional test results] ...

============================================================
  Test Summary
============================================================
Tests passed: 7
Tests failed: 0
Total tests: 7

✅ All tests passed!
```

## Using the MindsDB Client

### Basic Usage

```python
from mindsdb_client import MindsDBClient

# Create client (uses default configuration)
client = MindsDBClient()

# Check status
status = client.get_status()
print(f"Connected to MindsDB {status['mindsdb_version']}")

# Get all cities
cities = client.get_cities()
for city in cities:
    print(f"City: {city['name']}")

# Get specific city
bristol = client.get_city_by_name('Bristol')
print(bristol)

# Get city statistics (SERVICE19 data)
stats = client.get_city_statistics('Bristol')
print(f"Found {len(stats)} statistics records")

# Get data sources
sources = client.get_data_sources('Bristol')
print(f"Found {len(sources)} data sources")
```

### Custom Queries

```python
# Execute custom SQL query
result = client.execute_query(
    "SELECT * FROM urbanzero_postgres.cities WHERE country = 'UK';"
)

# Or use the helper method
results = client.custom_query(
    table="cities",
    where_clause="country = 'UK'",
    select_columns="name, population",
    limit=10
)
```

### Advanced Configuration

```python
from mindsdb_client import MindsDBClient, MindsDBConfig

# Custom configuration
config = MindsDBConfig(
    host="localhost",
    port=47334,
    datasource="urbanzero_postgres",
    use_https=False
)

client = MindsDBClient(config)
```

## Available Data

### Database: urbanzero_postgres

- **Type**: PostgreSQL
- **Host**: urbanzero-db.c5qeo4ayy5u5.eu-west-2.rds.amazonaws.com
- **SSL Mode**: require
- **Tables**: 54+ tables

### Key Tables

#### Core Tables
- `cities` - City information (Bristol, Manchester, Birmingham, Leeds, Edinburgh)
- `users` - User accounts
- `opportunities` - Investment opportunities
- `reports` - Generated reports

#### SERVICE19 Tables (City Research Data)
- `service19_city_data` - City statistics and metrics
- `service19_data_sources` - Data source tracking
- `service19_search_results` - Search results cache

#### AI & Integration Tables
- `ai_agents` - AI agent configurations
- `agent_data_flows` - Agent data flows
- `crew_execution_logs` - CrewAI execution logs
- `ckan_dataset_cache` - CKAN dataset cache

## Example Queries

### List all cities
```sql
SELECT * FROM urbanzero_postgres.cities;
```

### Get city by name
```sql
SELECT * FROM urbanzero_postgres.cities WHERE name = 'Bristol';
```

### Get SERVICE19 city data
```sql
SELECT * FROM urbanzero_postgres.service19_city_data WHERE city = 'Bristol';
```

### Get data sources for a city
```sql
SELECT * FROM urbanzero_postgres.service19_data_sources WHERE city = 'Bristol';
```

### Get investment opportunities
```sql
SELECT * FROM urbanzero_postgres.opportunities WHERE city = 'Bristol';
```

## Troubleshooting

### Issue: Connection refused / Cannot connect to MindsDB

**Cause**: SSH tunnel is not running or MindsDB is not accessible

**Solution**:
1. Verify SSH tunnel is running (check tunnel terminal)
2. If not running, restart tunnel using `setup_tunnel.ps1` or `start_tunnel.bat`
3. Verify MindsDB status: `curl http://localhost:47334/api/status`

### Issue: SSH key not found

**Cause**: SSH key file is missing or path is incorrect

**Solution**:
1. Verify key exists: `ls C:\Users\chriz\.ssh\cnz-staging-key.pem`
2. Check file permissions (should be readable only by you)
3. Contact admin if key is missing

### Issue: Port already in use

**Cause**: Another process is using port 47334 or tunnel is already running

**Solution**:
1. Check if tunnel is already running in another terminal
2. Check for other processes: `netstat -ano | findstr 47334`
3. Kill existing process or use existing tunnel

### Issue: Database/table not found

**Cause**: Incorrect database name or table name

**Solution**:
1. List available databases: `client.list_databases()`
2. List tables in database: `client.list_tables('urbanzero_postgres')`
3. Verify table name spelling and case

### Issue: Empty results

**Cause**: Table exists but has no data

**Solution**:
1. Verify table has data: `SELECT COUNT(*) FROM urbanzero_postgres.cities`
2. Check query filters (WHERE clause may be too restrictive)
3. Verify data was populated in the database

### Issue: Query timeout

**Cause**: Large dataset or slow connection

**Solution**:
1. Add LIMIT clause to queries
2. Use more specific WHERE clauses
3. Check network connection to EC2

## API Endpoints

### Status Check
```bash
curl http://localhost:47334/api/status
```

### List Databases
```bash
curl http://localhost:47334/api/databases/
```

### Execute SQL Query
```bash
curl -X POST http://localhost:47334/api/sql/query \
     -H "Content-Type: application/json" \
     -d '{"query": "SELECT * FROM urbanzero_postgres.cities LIMIT 5;"}'
```

## Files Reference

### Configuration Files
- `mindsdb_client.py` - Python client library for MindsDB
- `test_mindsdb_connection.py` - Comprehensive test suite
- `MINDSDB_SETUP.md` - Original setup documentation

### Tunnel Scripts
- `setup_tunnel.ps1` - PowerShell SSH tunnel setup
- `start_tunnel.bat` - Batch file SSH tunnel setup

### Documentation
- `SETUP_GUIDE.md` - This file
- `README.md` - Service23 overview

## Next Steps

1. **Start Development**: Use the MindsDB client in your Python scripts
2. **Integrate with Agents**: Connect to CrewAI agents for data analysis
3. **Build Queries**: Create custom queries for your use case
4. **Monitor Performance**: Track query performance and optimize as needed

## Support

For issues or questions:
1. Check this guide's troubleshooting section
2. Review `MINDSDB_SETUP.md` for additional details
3. Check MindsDB logs on EC2 instance
4. Contact the development team

## Important Notes

- **Keep SSH tunnel running** - MindsDB is only accessible when tunnel is active
- **Real data only** - All queries use actual PostgreSQL data, no simulated data
- **SSL required** - PostgreSQL connection requires SSL (sslmode=require)
- **No authentication** - MindsDB API has authentication disabled (local development)
- **5 UK cities available** - Bristol, Manchester, Birmingham, Leeds, Edinburgh

## Version Information

- **MindsDB Version**: 25.5.4.0
- **EC2 Instance**: 18.168.195.169
- **Database**: urbanzero-db.c5qeo4ayy5u5.eu-west-2.rds.amazonaws.com
- **Python Version**: 3.11+
- **Last Updated**: October 2025
