# MindsDB SSH Tunnel Setup Script
# Creates an SSH tunnel to the MindsDB instance on EC2

$SSH_KEY = "C:\Users\chriz\.ssh\cnz-staging-key.pem"
$EC2_HOST = "18.168.195.169"
$EC2_USER = "ec2-user"
$LOCAL_PORT = 47334
$REMOTE_PORT = 47334

Write-Host "Setting up SSH tunnel to MindsDB..." -ForegroundColor Cyan
Write-Host "EC2 Host: $EC2_HOST" -ForegroundColor Gray
Write-Host "Local Port: $LOCAL_PORT" -ForegroundColor Gray
Write-Host "Remote Port: $REMOTE_PORT" -ForegroundColor Gray
Write-Host ""

# Check if SSH key exists
if (-not (Test-Path $SSH_KEY)) {
    Write-Host "ERROR: SSH key not found at $SSH_KEY" -ForegroundColor Red
    exit 1
}

# Check if tunnel is already running
$existing = Get-NetTCPConnection -LocalPort $LOCAL_PORT -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "WARNING: Port $LOCAL_PORT is already in use" -ForegroundColor Yellow
    Write-Host "Attempting to connect anyway..." -ForegroundColor Yellow
}

Write-Host "Starting SSH tunnel (press Ctrl+C to stop)..." -ForegroundColor Green
Write-Host "Once connected, MindsDB will be available at http://localhost:$LOCAL_PORT" -ForegroundColor Green
Write-Host ""

# Start SSH tunnel
ssh -i $SSH_KEY -N -L "${LOCAL_PORT}:localhost:${REMOTE_PORT}" "${EC2_USER}@${EC2_HOST}"
