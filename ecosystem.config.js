module.exports = {
  apps: [
    {
      name: 'service23',
      script: 'api_server.py',
      interpreter: '.venv/bin/python',
      cwd: '/opt/service23',
      env: {
        PORT: 8023,
        HOST: '0.0.0.0',
        NODE_ENV: 'production'
      },
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: './logs/error.log',
      out_file: './logs/out.log',
      log_file: './logs/combined.log',
      time: true,
      merge_logs: true
    }
  ]
};
