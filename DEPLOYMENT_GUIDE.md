# SafeTNet Main Admin Panel - Production Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Configuration](#database-configuration)
4. [Docker Deployment](#docker-deployment)
5. [Manual Deployment](#manual-deployment)
6. [SSL/HTTPS Configuration](#sslhttps-configuration)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Backup and Recovery](#backup-and-recovery)
9. [Security Hardening](#security-hardening)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- **CPU**: 2+ cores
- **RAM**: 4GB+ (8GB recommended for production)
- **Storage**: 20GB+ available space
- **Network**: Ports 80, 443, 8000 (or custom ports)

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- PostgreSQL 13+ (if not using Docker)
- Redis 6+ (if not using Docker)
- Nginx (if not using Docker)
- Python 3.11+ (if not using Docker)

## Environment Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd SafeTNet
```

### 2. Environment Variables
Create `.env` file in the project root:

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost

# Database Configuration
DB_NAME=safetnet_db
DB_USER=safetnet_user
DB_PASSWORD=your-secure-db-password
DB_HOST=db
DB_PORT=5432

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Email Configuration (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=DENY

# CORS Settings
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 3. Generate Secret Keys
```bash
# Generate Django secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key)"

# Generate JWT secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Database Configuration

### PostgreSQL Setup (Manual)
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE safetnet_db;
CREATE USER safetnet_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE safetnet_db TO safetnet_user;
ALTER USER safetnet_user CREATEDB;
\q

# Configure PostgreSQL
sudo nano /etc/postgresql/13/main/postgresql.conf
# Set: listen_addresses = 'localhost'

sudo nano /etc/postgresql/13/main/pg_hba.conf
# Add: local   all             safetnet_user                    md5
```

## Docker Deployment

### 1. Production Docker Compose
Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build: .
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             python manage.py loaddata initial_data.json &&
             gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --max-requests 1000 SafeTNet.wsgi:application"
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - logs_volume:/app/logs
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/schema/"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.prod.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 3

  celery:
    build: .
    command: celery -A SafeTNet worker --loglevel=info --concurrency=4
    volumes:
      - logs_volume:/app/logs
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped

  celery-beat:
    build: .
    command: celery -A SafeTNet beat --loglevel=info
    volumes:
      - logs_volume:/app/logs
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped

volumes:
  postgres_data:
  static_volume:
  media_volume:
  logs_volume:
```

### 2. Deploy with Docker
```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up -d --build

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale web service
docker-compose -f docker-compose.prod.yml up -d --scale web=3
```

## Manual Deployment

### 1. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies
sudo apt install postgresql postgresql-contrib redis-server nginx
```

### 2. Database Migration
```bash
# Run migrations
python manage.py migrate

# Load seed data
python manage.py loaddata initial_data.json

# Create superuser
python manage.py createsuperuser
```

### 3. Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput
```

### 4. Gunicorn Configuration
Create `gunicorn.conf.py`:

```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

### 5. Systemd Service
Create `/etc/systemd/system/safetnet.service`:

```ini
[Unit]
Description=SafeTNet Admin Panel
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/SafeTNet
ExecStart=/path/to/venv/bin/gunicorn --config gunicorn.conf.py SafeTNet.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 6. Start Services
```bash
# Enable and start service
sudo systemctl enable safetnet
sudo systemctl start safetnet

# Check status
sudo systemctl status safetnet
```

## SSL/HTTPS Configuration

### 1. Let's Encrypt SSL
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. Nginx SSL Configuration
Update `nginx.prod.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## Monitoring and Logging

### 1. Log Configuration
Update Django settings for production logging:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/safetnet/django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/safetnet/error.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'users': {
            'handlers': ['file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### 2. Health Checks
Create health check endpoint:

```python
# In views.py
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    })
```

### 3. Monitoring with Prometheus (Optional)
```bash
# Install Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar xvfz prometheus-2.40.0.linux-amd64.tar.gz
cd prometheus-2.40.0.linux-amd64

# Configure prometheus.yml
# Start Prometheus
./prometheus --config.file=prometheus.yml
```

## Backup and Recovery

### 1. Database Backup
```bash
# Create backup script
cat > backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/safetnet"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -h localhost -U safetnet_user safetnet_db > $BACKUP_DIR/db_backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/db_backup_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete
EOF

chmod +x backup_db.sh

# Schedule daily backups
crontab -e
# Add: 0 2 * * * /path/to/backup_db.sh
```

### 2. Media Files Backup
```bash
# Backup media files
rsync -av /path/to/media/ /backup/location/media/
```

### 3. Recovery Process
```bash
# Restore database
gunzip db_backup_20240115_020000.sql.gz
psql -h localhost -U safetnet_user safetnet_db < db_backup_20240115_020000.sql

# Restore media files
rsync -av /backup/location/media/ /path/to/media/
```

## Security Hardening

### 1. Firewall Configuration
```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Fail2Ban Configuration
```bash
# Install Fail2Ban
sudo apt install fail2ban

# Configure for Django
sudo nano /etc/fail2ban/jail.local
```

Add to jail.local:
```ini
[django-auth]
enabled = true
port = 80,443
filter = django-auth
logpath = /var/log/safetnet/error.log
maxretry = 5
bantime = 3600
```

### 3. Database Security
```bash
# PostgreSQL security
sudo nano /etc/postgresql/13/main/postgresql.conf
# Set: ssl = on
# Set: log_statement = 'all'
# Set: log_min_duration_statement = 1000

sudo nano /etc/postgresql/13/main/pg_hba.conf
# Restrict access to specific IPs
```

### 4. Application Security
```python
# In settings.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U safetnet_user -d safetnet_db

# Check logs
sudo tail -f /var/log/postgresql/postgresql-13-main.log
```

#### 2. Application Not Starting
```bash
# Check application logs
sudo journalctl -u safetnet -f

# Check Django logs
tail -f /var/log/safetnet/django.log

# Test Django
python manage.py check --deploy
```

#### 3. Nginx Issues
```bash
# Check Nginx status
sudo systemctl status nginx

# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

#### 4. Performance Issues
```bash
# Check system resources
htop
df -h
free -h

# Check database performance
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Monitor logs
tail -f /var/log/safetnet/django.log | grep ERROR
```

### Performance Optimization

#### 1. Database Optimization
```sql
-- Create indexes
CREATE INDEX CONCURRENTLY idx_alerts_created_at ON users_alert(created_at);
CREATE INDEX CONCURRENTLY idx_alerts_severity ON users_alert(severity);
CREATE INDEX CONCURRENTLY idx_alerts_organization ON users_alert(geofence_id);

-- Analyze tables
ANALYZE users_alert;
ANALYZE users_geofence;
ANALYZE users_user;
```

#### 2. Application Optimization
```python
# Use database connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'safetnet_db',
        'USER': 'safetnet_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'MAX_CONNS': 20,
            'MIN_CONNS': 5,
        }
    }
}

# Enable caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### Maintenance Tasks

#### 1. Regular Maintenance Script
```bash
cat > maintenance.sh << 'EOF'
#!/bin/bash
# Daily maintenance tasks

# Clean old logs
find /var/log/safetnet -name "*.log" -mtime +30 -delete

# Optimize database
sudo -u postgres psql safetnet_db -c "VACUUM ANALYZE;"

# Check disk space
df -h | awk '$5 > 80 {print $0}'

# Check memory usage
free -h | awk 'NR==2{printf "Memory Usage: %s/%s (%.2f%%)\n", $3,$2,$3*100/$2 }'

# Check service status
systemctl is-active safetnet
systemctl is-active nginx
systemctl is-active postgresql
EOF

chmod +x maintenance.sh
```

#### 2. Monitoring Script
```bash
cat > monitor.sh << 'EOF'
#!/bin/bash
# System monitoring

# Check if services are running
if ! systemctl is-active --quiet safetnet; then
    echo "SafeTNet service is down!"
    systemctl restart safetnet
fi

if ! systemctl is-active --quiet nginx; then
    echo "Nginx service is down!"
    systemctl restart nginx
fi

# Check disk space
if [ $(df / | awk 'NR==2 {print $5}' | sed 's/%//') -gt 80 ]; then
    echo "Disk space is low!"
fi

# Check memory usage
if [ $(free | awk 'NR==2{printf "%.0f", $3*100/$2}') -gt 80 ]; then
    echo "Memory usage is high!"
fi
EOF

chmod +x monitor.sh
```

## Conclusion

This deployment guide provides comprehensive instructions for deploying the SafeTNet Main Admin Panel in a production environment. Follow the steps carefully and adapt them to your specific infrastructure requirements.

For additional support or questions, refer to the troubleshooting section or contact the development team.
