module.exports = {
  apps: [{
    name: 'service23_data_analyst',
    script: '.venv/bin/python',
    args: 'api_server.py',
    cwd: '/opt/service23_data_analyst',
    interpreter: 'none',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '2G',
    env: {
      NODE_ENV: 'production',
      PORT: 8023,
      PYTHONPATH: '/opt/service23_data_analyst'
    },
    error_file: '/opt/service23_data_analyst/logs/error.log',
    out_file: '/opt/service23_data_analyst/logs/out.log',
    log_file: '/opt/service23_data_analyst/logs/combined.log',
    time: true
  }]
};
