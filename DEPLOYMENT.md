# Service23 Deployment Guide

## Overview

Service23 is the Data Analyst Agent API powered by Claude SDK, providing intelligent data analysis capabilities across PostgreSQL and MindsDB. The service runs on port 8023.

## Quick Start

### Local Development

```bash
# Create virtual environment
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the service
./run.sh
# or
python api_server.py
```

The service will be available at http://localhost:8023

## Production Deployment

### Option 1: PM2 (Recommended)

```bash
# Install to /opt/service23
sudo mkdir -p /opt/service23
sudo cp -r . /opt/service23/
cd /opt/service23

# Setup virtual environment
uv venv
source .venv/bin/activate
pip install -r requirements.txt

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup  # Follow the instructions to enable auto-start on boot

# Check status
pm2 status service23
pm2 logs service23
```

### Option 2: Direct Shell Script

```bash
# Run in background
nohup ./run.sh > service23.log 2>&1 &

# Or with screen/tmux
screen -S service23
./run.sh
# Ctrl+A, D to detach
```

## Nginx Configuration

### Step 1: Add upstream to nginx.conf

Add this to your main nginx configuration file (usually `/etc/nginx/nginx.conf` or `/etc/nginx/sites-available/default`):

```nginx
upstream service23_app {
    server localhost:8023;
}
```

### Step 2: Add location block

Add this location block to expose the service:

```nginx
location /api/service23/ {
    rewrite ^/api/service23/(.*) /$1 break;

    proxy_pass http://service23_app;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;

    # Increase timeout for long-running AI operations
    proxy_read_timeout 300s;
    proxy_connect_timeout 75s;
}
```

### Step 3: Test and reload nginx

```bash
# Test configuration
sudo nginx -t

# Reload nginx
sudo nginx -s reload
# or
sudo systemctl reload nginx
```

## API Endpoints

Once deployed, the service will be accessible at:

- **Local**: http://localhost:8023
- **Via Nginx**: https://yourdomain.com/api/service23/

### Available Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `POST /api/query` - Query the data analyst agent
- `POST /api/postgres/add-column` - Add column to PostgreSQL table
- `GET /api/postgres/tables` - List all tables
- `GET /api/postgres/schema/{table}` - Get table schema
- `POST /api/analyze/city-insights` - Generate city insights analysis

## Environment Variables

Required environment variables (set in `.env` file):

```bash
# Service Configuration
PORT=8023
HOST=0.0.0.0

# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# AI Services
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key  # If using OpenAI models

# MindsDB (optional)
MINDSDB_URL=https://cloud.mindsdb.com
MINDSDB_USERNAME=your_username
MINDSDB_PASSWORD=your_password
```

## Testing the Deployment

```bash
# Health check
curl http://localhost:8023/health

# Via nginx (after nginx configuration)
curl https://yourdomain.com/api/service23/health

# Test query endpoint
curl -X POST http://localhost:8023/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How many records are in service19_onboarding_data?"}'

# Test city insights
curl -X POST http://localhost:8023/api/analyze/city-insights \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Bristol",
    "country_code": "GB",
    "success_criteria": "Achieve net zero by 2030"
  }'
```

## Monitoring

### PM2 Commands

```bash
# View logs
pm2 logs service23

# Restart service
pm2 restart service23

# Stop service
pm2 stop service23

# View resource usage
pm2 monit
```

### Log Files

PM2 logs are stored in:
- Error log: `./logs/error.log`
- Output log: `./logs/out.log`
- Combined log: `./logs/combined.log`

## Troubleshooting

### Service won't start

1. Check if port 8023 is available:
   ```bash
   lsof -i :8023
   # or
   netstat -tlnp | grep 8023
   ```

2. Check virtual environment:
   ```bash
   source .venv/bin/activate
   python -c "import fastapi; print('FastAPI OK')"
   ```

3. Check environment variables:
   ```bash
   grep -v '^#' .env
   ```

### Database connection issues

1. Test PostgreSQL connection:
   ```bash
   python test_mindsdb_connection.py
   ```

2. Check DATABASE_URL format:
   ```
   postgresql://user:password@host:5432/database?sslmode=require
   ```

### Nginx 502 Bad Gateway

1. Check if service is running:
   ```bash
   pm2 status service23
   curl http://localhost:8023/health
   ```

2. Check nginx error logs:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

3. Verify upstream configuration in nginx.conf

## Integration with Other Services

Service23 integrates with:
- **Service19**: Onboarding data analysis
- **Service6**: Voice/chat success criteria
- **PostgreSQL**: Direct database queries
- **MindsDB**: ML-powered insights
- **Claude SDK**: AI agent orchestration

## Security Considerations

1. Always use HTTPS in production (configure nginx SSL)
2. Set up firewall rules to restrict access to port 8023
3. Use environment variables for sensitive credentials
4. Regularly update dependencies
5. Monitor API usage and implement rate limiting if needed

## Updates and Maintenance

```bash
# Pull latest code
cd /opt/service23
git pull

# Update dependencies
source .venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart service
pm2 restart service23
```
