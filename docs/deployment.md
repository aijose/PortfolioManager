# Deployment and Configuration Guide

## Table of Contents

1. [Deployment Options](#deployment-options)
2. [Local Development Setup](#local-development-setup)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Security Considerations](#security-considerations)
7. [Performance Optimization](#performance-optimization)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Backup and Recovery](#backup-and-recovery)
10. [Maintenance](#maintenance)

## Deployment Options

### Overview

Portfolio Manager is designed as a **single-user local application** with several deployment options:

1. **Local Development** - For development and testing
2. **Local Production** - For personal use on local machine
3. **Network Deployment** - For access within local network
4. **Docker Deployment** - Containerized deployment
5. **Cloud Deployment** - VPS or cloud instance (advanced)

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Browser                       │
│                 (localhost:8000)                        │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                FastAPI Application                     │
│                 (uvicorn server)                        │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                SQLite Database                         │
│              (local file storage)                       │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│               External APIs                             │
│        (Yahoo Finance, Polygon.io)                      │
└─────────────────────────────────────────────────────────┘
```

## Local Development Setup

### Prerequisites

- Python 3.9 or higher
- 2GB RAM minimum, 4GB recommended
- 1GB free disk space
- Internet connection for stock data

### Quick Setup

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd PortfolioManager
   ```

2. **Install Dependencies**
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **Create Environment File**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Start Development Server**
   ```bash
   uv run uvicorn web_server.app:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access Application**
   - Open browser: `http://localhost:8000`

### Development Configuration

**`.env` file:**
```bash
# Development settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Database
DATABASE_URL=sqlite:///data/portfolio_manager.db

# API Keys (optional)
POLYGON_API_KEY=your_polygon_key_here

# Server settings
HOST=0.0.0.0
PORT=8000
```

## Production Deployment

### Local Production Setup

For personal use on your local machine:

1. **Production Environment**
   ```bash
   # Create production environment
   export ENVIRONMENT=production
   export DEBUG=false
   export LOG_LEVEL=INFO
   ```

2. **Install Production Dependencies**
   ```bash
   # Install with production extras
   uv sync --no-dev
   ```

3. **Optimize Database**
   ```bash
   # Create data directory
   mkdir -p data
   chmod 755 data
   
   # Optimize SQLite
   sqlite3 data/portfolio_manager.db "PRAGMA optimize;"
   ```

4. **Start Production Server**
   ```bash
   # Using Gunicorn (recommended for production)
   uv add gunicorn
   uv run gunicorn web_server.app:app -w 2 -k uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:8000 --timeout 120
   
   # Or using Uvicorn directly
   uv run uvicorn web_server.app:app --host 0.0.0.0 --port 8000 \
     --workers 2 --no-reload
   ```

### Network Deployment

To make the application accessible from other devices on your network:

1. **Configure Network Access**
   ```bash
   # Find your local IP
   ip addr show  # Linux
   ifconfig      # Mac
   ipconfig      # Windows
   ```

2. **Start Server with Network Binding**
   ```bash
   uv run uvicorn web_server.app:app --host 0.0.0.0 --port 8000
   ```

3. **Configure Firewall** (if needed)
   ```bash
   # Linux (ufw)
   sudo ufw allow 8000
   
   # Or specific IP range
   sudo ufw allow from 192.168.1.0/24 to any port 8000
   ```

4. **Access from Network**
   - From other devices: `http://YOUR_LOCAL_IP:8000`
   - Example: `http://192.168.1.100:8000`

### Systemd Service (Linux)

For automatic startup on Linux systems:

1. **Create Service File**
   ```bash
   sudo nano /etc/systemd/system/PortfolioManager.service
   ```

2. **Service Configuration**
   ```ini
   [Unit]
   Description=Portfolio Manager Web Application
   After=network.target
   
   [Service]
   Type=exec
   User=your_username
   Group=your_group
   WorkingDirectory=/path/to/PortfolioManager
   Environment=PATH=/path/to/PortfolioManager/.venv/bin
   Environment=ENVIRONMENT=production
   Environment=DATABASE_URL=sqlite:///data/portfolio_manager.db
   ExecStart=/path/to/PortfolioManager/.venv/bin/uvicorn web_server.app:app --host 0.0.0.0 --port 8000
   Restart=always
   RestartSec=3
   
   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and Start Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable PortfolioManager
   sudo systemctl start PortfolioManager
   sudo systemctl status PortfolioManager
   ```

## Docker Deployment

### Dockerfile

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p data && chmod 755 data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "web_server.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  PortfolioManager:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - DATABASE_URL=sqlite:///data/portfolio_manager.db
      - POLYGON_API_KEY=${POLYGON_API_KEY}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  portfolio_data:
  portfolio_logs:
```

### Docker Commands

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build

# Access shell
docker-compose exec PortfolioManager bash
```

### Docker with Bind Mounts

For persistent data:

```bash
# Create local directories
mkdir -p data logs

# Run with bind mounts
docker run -d \
  --name PortfolioManager \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e ENVIRONMENT=production \
  PortfolioManager:latest
```

## Environment Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Deployment environment | `development` | No |
| `DEBUG` | Enable debug mode | `false` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `HOST` | Server host | `0.0.0.0` | No |
| `PORT` | Server port | `8000` | No |
| `DATABASE_URL` | Database connection string | `sqlite:///data/portfolio_manager.db` | No |
| `POLYGON_API_KEY` | Polygon.io API key | None | No |
| `CACHE_DURATION` | Price cache duration (seconds) | `300` | No |
| `NEWS_CACHE_DURATION` | News cache duration (seconds) | `14400` | No |

### Configuration Files

**`.env` file example:**
```bash
# Application settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Server configuration
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///data/portfolio_manager.db

# External APIs
POLYGON_API_KEY=your_api_key_here

# Cache settings
CACHE_DURATION=300
NEWS_CACHE_DURATION=14400

# Security (if implementing authentication)
SECRET_KEY=your_secret_key_here
```

### Configuration Validation

The application validates configuration on startup:

```python
# config/settings.py
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    
    @validator('log_level')
    def validate_log_level(cls, v):
        if v not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            raise ValueError('Invalid log level')
        return v
```

## Security Considerations

### Local Deployment Security

**Data Protection:**
- All data stored locally by default
- No external data transmission except API calls
- SQLite database file permissions: 664

**Network Security:**
```bash
# Bind to localhost only for local use
HOST=127.0.0.1

# Or specific interface
HOST=192.168.1.100
```

**API Key Security:**
```bash
# Store API keys in environment variables
export POLYGON_API_KEY="your_key_here"

# Or in .env file (not committed to git)
echo "POLYGON_API_KEY=your_key_here" >> .env
```

### Network Deployment Security

**Firewall Configuration:**
```bash
# Linux (ufw)
sudo ufw allow from 192.168.1.0/24 to any port 8000
sudo ufw deny 8000  # Block external access

# Or use specific IP addresses
sudo ufw allow from 192.168.1.50 to any port 8000
```

**Reverse Proxy (Optional):**

Nginx configuration for additional security:

```nginx
server {
    listen 80;
    server_name portfolio.local;
    
    # IP whitelist
    allow 192.168.1.0/24;
    deny all;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### HTTPS Configuration (Optional)

For enhanced security over network:

1. **Generate Self-Signed Certificate**
   ```bash
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
   ```

2. **Start with HTTPS**
   ```bash
   uvicorn web_server.app:app --host 0.0.0.0 --port 8443 \
     --ssl-keyfile key.pem --ssl-certfile cert.pem
   ```

## Performance Optimization

### Application Optimization

**Database Optimization:**
```bash
# SQLite optimizations
sqlite3 data/portfolio_manager.db << EOF
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=10000;
PRAGMA temp_store=memory;
PRAGMA mmap_size=268435456;
EOF
```

**Caching Configuration:**
```python
# Increase cache durations for production
CACHE_DURATION=600  # 10 minutes for prices
NEWS_CACHE_DURATION=21600  # 6 hours for news
```

**Server Configuration:**
```bash
# Multiple workers for production
gunicorn web_server.app:app -w 4 -k uvicorn.workers.UvicornWorker \
  --worker-connections 1000 --max-requests 10000
```

### System Optimization

**Memory Settings:**
```bash
# Linux: Optimize for SQLite
echo 'vm.swappiness=10' >> /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' >> /etc/sysctl.conf
```

**File Descriptors:**
```bash
# Increase limits if needed
ulimit -n 4096
```

### CDN and Static Files

For network deployment, serve static files separately:

```nginx
server {
    # ... other config ...
    
    location /static/ {
        alias /path/to/PortfolioManager/src/web_server/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        # ... proxy config ...
    }
}
```

## Monitoring and Logging

### Logging Configuration

**Production Logging:**
```python
# logging_config.py
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/portfolio_manager.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["default"],
    },
}
```

**Log Rotation:**
```bash
# Setup logrotate
sudo nano /etc/logrotate.d/PortfolioManager

# Configuration
/path/to/PortfolioManager/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 username username
}
```

### Health Monitoring

**Health Check Endpoint:**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "database": "connected" if check_db() else "disconnected"
    }
```

**System Monitoring Script:**
```bash
#!/bin/bash
# monitor.sh

check_service() {
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "$(date): Portfolio Manager is healthy"
    else
        echo "$(date): Portfolio Manager is DOWN"
        # Restart service
        systemctl restart PortfolioManager
    fi
}

# Run every 5 minutes
while true; do
    check_service
    sleep 300
done
```

### Performance Monitoring

**Resource Usage:**
```bash
# Monitor script
#!/bin/bash
while true; do
    echo "$(date): $(ps -p $(pgrep -f portfolio) -o pid,%cpu,%mem,cmd --no-headers)"
    sleep 60
done >> logs/resource_usage.log
```

## Backup and Recovery

### Database Backup

**Automated Backup Script:**
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/path/to/backups"
DB_PATH="/path/to/PortfolioManager/data/portfolio_manager.db"
DATE=$(date +"%Y%m%d_%H%M%S")

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
sqlite3 "$DB_PATH" ".backup $BACKUP_DIR/portfolio_backup_$DATE.db"

# Compress backup
gzip "$BACKUP_DIR/portfolio_backup_$DATE.db"

# Keep only last 30 backups
find "$BACKUP_DIR" -name "portfolio_backup_*.db.gz" -mtime +30 -delete

echo "Backup completed: portfolio_backup_$DATE.db.gz"
```

**Cron Job Setup:**
```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /path/to/backup.sh >> /var/log/portfolio_backup.log 2>&1
```

### Configuration Backup

**Backup Script for Full System:**
```bash
#!/bin/bash
# full_backup.sh

BACKUP_DIR="/path/to/backups"
APP_DIR="/path/to/PortfolioManager"
DATE=$(date +"%Y%m%d_%H%M%S")

# Create backup archive
tar -czf "$BACKUP_DIR/portfolio_full_backup_$DATE.tar.gz" \
    -C "$APP_DIR" \
    data/ \
    .env \
    logs/ \
    --exclude='logs/*.log'

echo "Full backup completed: portfolio_full_backup_$DATE.tar.gz"
```

### Recovery Procedures

**Database Recovery:**
```bash
# Restore from backup
gunzip portfolio_backup_20250106_020000.db.gz
cp portfolio_backup_20250106_020000.db data/portfolio_manager.db

# Verify integrity
sqlite3 data/portfolio_manager.db "PRAGMA integrity_check;"
```

**Full System Recovery:**
```bash
# Extract backup
tar -xzf portfolio_full_backup_20250106_020000.tar.gz

# Restore permissions
chmod 755 data/
chmod 664 data/portfolio_manager.db
```

## Maintenance

### Regular Maintenance Tasks

**Daily:**
- Monitor logs for errors
- Check disk space
- Verify backup completion

**Weekly:**
- Review performance metrics
- Update stock symbols if needed
- Clean old log files

**Monthly:**
- Update dependencies
- Optimize database
- Review security settings

### Update Procedures

**Application Updates:**
```bash
# Backup current version
cp -r PortfolioManager PortfolioManager-backup

# Pull updates
git pull origin main

# Update dependencies
uv sync

# Restart service
systemctl restart PortfolioManager
```

**Dependency Updates:**
```bash
# Check for updates
uv outdated

# Update specific package
uv update fastapi

# Update all packages
uv update
```

### Database Maintenance

**Regular Optimization:**
```bash
# SQLite maintenance
sqlite3 data/portfolio_manager.db << EOF
PRAGMA optimize;
VACUUM;
REINDEX;
EOF
```

**Size Monitoring:**
```bash
# Monitor database size
du -h data/portfolio_manager.db

# Monitor growth over time
echo "$(date): $(du -h data/portfolio_manager.db)" >> logs/db_size.log
```

---

For more deployment-specific questions, see:
- [Troubleshooting Guide](troubleshooting.md)
- [Developer Guide](developer-guide.md)
- [API Reference](api-reference.md)