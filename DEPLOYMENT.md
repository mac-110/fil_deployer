# Deployment Guide

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fil_deployer
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and set your values
   ```

3. **Generate encryption secret**
   ```bash
   # Generate a strong random secret
   openssl rand -base64 32

   # Add to .env file
   echo "ENCRYPTION_SECRET=<generated-secret>" >> .env
   ```

4. **Install backend dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

5. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

6. **Run the application**
   ```bash
   # Terminal 1: Backend
   cd backend
   uvicorn app.main:app --reload

   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

7. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Default credentials: admin / admin

---

## Docker Deployment

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

### Steps

1. **Set environment variables**
   ```bash
   # Create .env file
   cat > .env << 'EOF'
   ENCRYPTION_SECRET=$(openssl rand -base64 32)
   SESSION_SECRET=$(openssl rand -base64 32)
   GITLAB_GROUP_TOKEN=your-gitlab-token
   ARTIFACTORY_TOKEN=your-artifactory-token
   EOF
   ```

   Or manually:
   ```bash
   cp .env.example .env
   # Edit .env and fill in values
   ```

2. **Build and run**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Application: http://localhost:8081
   - Default credentials: admin / admin

4. **View logs**
   ```bash
   docker-compose logs -f
   ```

5. **Stop the application**
   ```bash
   docker-compose down
   ```

---

## Production Deployment

### Security Checklist

Before deploying to production, ensure:

- [ ] **Set custom `ENCRYPTION_SECRET`**
  ```bash
  export ENCRYPTION_SECRET=$(openssl rand -base64 32)
  ```

- [ ] **Set custom `SESSION_SECRET`**
  ```bash
  export SESSION_SECRET=$(openssl rand -base64 32)
  ```

- [ ] **Change default admin password**
  - Login with admin/admin
  - Go to Users → Change admin password

- [ ] **Configure GitLab token** via Settings UI

- [ ] **Configure Artifactory token** via Settings UI

- [ ] **Restrict file permissions**
  ```bash
  chmod 600 config/app_config.json
  chmod 600 config/users.json
  chmod 600 .env
  ```

- [ ] **Enable HTTPS** (reverse proxy recommended)

- [ ] **Set up backup** for config/ directory

### Environment Variables

Required environment variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENCRYPTION_SECRET` | Secret for encrypting tokens | ⚠️ Default | ✅ Yes |
| `SESSION_SECRET` | Secret for session cookies | `change-me-in-production` | ✅ Yes |
| `BACKEND_URL` | Backend URL | `http://localhost:8000` | No |
| `FRONTEND_URL` | Frontend URL (CORS) | `http://localhost:3000` | No |
| `GITLAB_URL` | GitLab instance URL | `https://code.swisscom.com` | No* |
| `GITLAB_GROUP_TOKEN` | GitLab API token | - | No* |
| `ARTIFACTORY_URL` | Artifactory URL | `https://bin.swisscom.com` | No* |
| `ARTIFACTORY_TOKEN` | Artifactory API token | - | No* |

\* Can be configured via Settings UI

### Docker Production Configuration

**docker-compose.prod.yml:**
```yaml
version: '3.8'

services:
  fil-deployer:
    build: .
    ports:
      - "8081:80"
    environment:
      - ENCRYPTION_SECRET=${ENCRYPTION_SECRET}
      - SESSION_SECRET=${SESSION_SECRET}
      - GITLAB_URL=https://code.swisscom.com
      - BACKEND_URL=https://your-domain.com
      - FRONTEND_URL=https://your-domain.com
      - CONFIG_FILE=/app/config/customers.json
      - GIT_CACHE_DIR=/tmp/fil-deployer-repos
    volumes:
      - ./config:/app/config
      - git-cache:/tmp/fil-deployer-repos
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  git-cache:
```

Run with:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Reverse Proxy (nginx)

**nginx.conf:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://localhost:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Backup and Recovery

### Backup

Backup the following directories:

```bash
# Create backup
tar -czf fil-deployer-backup-$(date +%Y%m%d).tar.gz \
  config/ \
  .env

# Store securely (encrypted recommended)
gpg -c fil-deployer-backup-$(date +%Y%m%d).tar.gz
```

### Recovery

```bash
# Extract backup
tar -xzf fil-deployer-backup-20240101.tar.gz

# Restore config
cp -r config/ /path/to/fil_deployer/
cp .env /path/to/fil_deployer/

# Restart application
docker-compose restart
```

---

## Monitoring

### Health Checks

```bash
# Backend API health
curl http://localhost:8000/

# Check logs
docker-compose logs -f fil-deployer
```

### Log Files

Logs are output to stdout/stderr. View with:

```bash
docker-compose logs --tail=100 -f
```

---

## Troubleshooting

### "Failed to decrypt token" Error

**Cause:** `ENCRYPTION_SECRET` changed or tokens encrypted with different key

**Solution:**
1. Check if `ENCRYPTION_SECRET` environment variable is set correctly
2. If changed, re-enter all tokens via Settings UI
3. Or restore old `ENCRYPTION_SECRET` from backup

### "Using default encryption secret" Warning

**Cause:** `ENCRYPTION_SECRET` not set

**Solution:**
```bash
export ENCRYPTION_SECRET=$(openssl rand -base64 32)
# Restart application
```

### Docker Build Fails

**Solution:**
```bash
# Clear Docker cache
docker-compose down
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

### Permission Denied on Config Files

**Solution:**
```bash
# Fix ownership (inside Docker)
docker-compose exec fil-deployer chown -R app:app /app/config

# Or on host
sudo chown -R $USER:$USER config/
```

---

## Updating

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild Docker image
docker-compose down
docker-compose build
docker-compose up -d
```

### Database Migrations

Currently using JSON files (no migrations needed).
Config files are automatically migrated on startup.

---

## Support

For issues or questions:
- Check [SECURITY.md](SECURITY.md) for security-related topics
- Check [README.md](README.md) for general documentation
- Open an issue on GitHub
