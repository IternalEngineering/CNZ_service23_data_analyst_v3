# MindsDB Connection Status

## ✅ Connection Established Successfully

**Date**: October 14, 2025
**Service**: service23 (Data Analyst Agent)

## Connection Details

### SSH Tunnel
- **EC2 Host**: 18.168.195.169
- **EC2 User**: ec2-user
- **SSH Key**: `C:\Users\chriz\.ssh\cnz-staging-key.pem`
- **Local Port**: 47334
- **Remote Port**: 47334
- **Status**: Active and running in background

### MindsDB Server
- **Version**: 25.5.4.0
- **Environment**: local
- **Authentication**: Disabled (development mode)
- **URL**: http://localhost:47334

### Database Connection
- **Name**: urbanzero_postgres
- **Type**: PostgreSQL
- **Host**: urbanzero-db.c5qeo4ayy5u5.eu-west-2.rds.amazonaws.com
- **Database**: urbanzero-db
- **SSL Mode**: require
- **Status**: Connected and operational

## Verified Features

### ✅ Working Features
1. **MindsDB Status API** - Responding correctly
2. **Database Listing** - 10 databases found
3. **Table Access** - 130 tables accessible
4. **Cities Table** - 5 UK cities available:
   - Bristol (pop: 463,400)
   - Manchester (pop: 547,627)
   - Birmingham (pop: 1,141,816)
   - Leeds (pop: 793,139)
   - Edinburgh (pop: 524,930)
5. **SQL Queries** - Successfully executing queries

### 📊 Available Tables
- `cities` - City master data
- `users` - User accounts
- `opportunities` - Investment opportunities
- `service19_city_data` - City statistics (empty)
- `service19_data_sources` - Data sources (empty)
- Plus 125+ additional tables

## Quick Start Commands

### Start SSH Tunnel

**PowerShell:**
```powershell
cd C:\Users\chriz\OneDrive\Documents\CNZ\UrbanZero2\UrbanZero\server_c\service23
.\setup_tunnel.ps1
```

**Batch:**
```batch
cd C:\Users\chriz\OneDrive\Documents\CNZ\UrbanZero2\UrbanZero\server_c\service23
start_tunnel.bat
```

**Manual SSH:**
```bash
ssh -i C:\Users\chriz\.ssh\cnz-staging-key.pem -N -L 47334:localhost:47334 ec2-user@18.168.195.169
```

### Verify Connection

**Using Python:**
```bash
cd C:\Users\chriz\OneDrive\Documents\CNZ\UrbanZero2\UrbanZero\server_c\service23
python verify_mindsdb.py
```

**Using curl:**
```bash
curl http://localhost:47334/api/status
```

## Example Queries

### List All Cities
```sql
SELECT name, country, population FROM urbanzero_postgres.cities;
```

### Get City by Name
```sql
SELECT * FROM urbanzero_postgres.cities WHERE name = 'Bristol';
```

### Count Tables
```sql
SHOW TABLES FROM urbanzero_postgres;
```

### Check SERVICE19 Data
```sql
SELECT city, COUNT(*) as record_count
FROM urbanzero_postgres.service19_city_data
GROUP BY city;
```

## API Endpoints

### Status Check
```bash
curl http://localhost:47334/api/status
```

### List Databases
```bash
curl http://localhost:47334/api/databases/
```

### Execute Query
```bash
curl -X POST http://localhost:47334/api/sql/query \
     -H "Content-Type: application/json" \
     -d '{"query": "SELECT * FROM urbanzero_postgres.cities LIMIT 5;"}'
```

## Python Integration

### Using MindsDB Client
```python
from mindsdb_client import MindsDBClient

# Initialize client
client = MindsDBClient(
    host='localhost',
    port=47334,
    datasource='urbanzero_postgres'
)

# Get status
status = client.get_status()
print(f"Connected to MindsDB {status['mindsdb_version']}")

# Get cities
cities = client.get_cities()
for city in cities:
    print(f"City: {city['name']}")

# Get city by name
bristol = client.get_city_by_name('Bristol')
print(bristol)
```

### Direct HTTP Requests
```python
import requests

# Check status
response = requests.get('http://localhost:47334/api/status')
status = response.json()
print(status)

# Execute query
query = "SELECT * FROM urbanzero_postgres.cities LIMIT 5;"
response = requests.post(
    'http://localhost:47334/api/sql/query',
    json={'query': query}
)
results = response.json()
print(results)
```

## Troubleshooting

### Tunnel Not Running
```bash
# Check if port is in use
netstat -ano | findstr 47334

# If tunnel is not running, start it
.\setup_tunnel.ps1
```

### Connection Timeout
1. Verify SSH tunnel is active
2. Check MindsDB is running on EC2
3. Verify firewall rules allow SSH tunnel

### Query Errors
1. Verify table name: `SHOW TABLES FROM urbanzero_postgres;`
2. Check column names: `DESCRIBE urbanzero_postgres.cities;`
3. Ensure proper SQL syntax for PostgreSQL

### Database Not Found
1. List databases: `curl http://localhost:47334/api/databases/`
2. Verify 'urbanzero_postgres' is in the list
3. Check database configuration on MindsDB server

## Next Steps

1. **Populate SERVICE19 Tables**: The `service19_city_data` and `service19_data_sources` tables are empty and ready for data
2. **Integrate with Agents**: Connect the data analyst agent to use MindsDB queries
3. **Add MindsDB Models**: Create ML models for predictions and analysis
4. **Set Up Automated Queries**: Schedule regular data updates via MindsDB

## Files

- `setup_tunnel.ps1` - PowerShell tunnel setup script
- `start_tunnel.bat` - Batch tunnel setup script
- `verify_mindsdb.py` - Connection verification script
- `test_mindsdb_connection.py` - Comprehensive test suite
- `mindsdb_client.py` - Python client library
- `MINDSDB_SETUP.md` - Detailed setup guide
- `MINDSDB_CONNECTION_STATUS.md` - This status document

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in the SSH tunnel output
3. Verify EC2 instance is running
4. Check database credentials in `.env` file
