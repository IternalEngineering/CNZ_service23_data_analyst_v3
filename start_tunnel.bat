@echo off
REM MindsDB SSH Tunnel Setup Script (Windows Batch)
REM Creates an SSH tunnel to the MindsDB instance on EC2

set SSH_KEY=C:\Users\chriz\.ssh\cnz-staging-key.pem
set EC2_HOST=18.168.195.169
set EC2_USER=ec2-user
set LOCAL_PORT=47334
set REMOTE_PORT=47334

echo.
echo ========================================
echo MindsDB SSH Tunnel Setup
echo ========================================
echo EC2 Host: %EC2_HOST%
echo Local Port: %LOCAL_PORT%
echo Remote Port: %REMOTE_PORT%
echo ========================================
echo.

REM Check if SSH key exists
if not exist "%SSH_KEY%" (
    echo ERROR: SSH key not found at %SSH_KEY%
    pause
    exit /b 1
)

echo Starting SSH tunnel...
echo Press Ctrl+C to stop the tunnel
echo.
echo Once connected, MindsDB will be available at:
echo http://localhost:%LOCAL_PORT%
echo.

REM Start SSH tunnel
ssh -i "%SSH_KEY%" -N -L %LOCAL_PORT%:localhost:%REMOTE_PORT% %EC2_USER%@%EC2_HOST%
