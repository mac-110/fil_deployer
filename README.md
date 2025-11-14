# FIL Deployer

A web application for managing FIL deployments by editing services.csv files across multiple customer repositories and stages. Built with FastAPI, React, and Docker.

## Features

- **Simple Authentication**: Username/password login (default: admin/admin)
- **User Management**: Create and manage users within the app
- **GitLab Token Configuration**: Configure GitLab Group Access Token in the UI
- **Multi-Customer Support**: Manage multiple customer repositories
- **Stage Management**: Deploy to different stages (dev, tst, prd, etc.)
- **Service Editor**: Easy-to-use interface for editing services
- **Automatic Git Operations**: Creates feature branches and merge requests automatically
- **User-Friendly UI**: Display simplified service names and versions
- **Admin Panel**: Manage users, customers, and GitLab tokens
- **Token Encryption**: Automatic encryption of sensitive tokens at rest

## Architecture

- **Backend**: Python FastAPI with GitLab API integration
- **Frontend**: React with TypeScript
- **Deployment**: Docker container with Nginx reverse proxy
- **Authentication**: Simple username/password with session management
- **User Storage**: JSON-based user database
- **Security**: Fernet symmetric encryption for tokens at rest

## Prerequisites

- Docker and Docker Compose
- GitLab group access token with API and write_repository permissions

## Quick Start

### 1. Clone the Repository

```bash
cd /path/to/fil_deployer
```

### 2. Create Environment File

```bash
cp .env.example .env
```

**Generate secure secrets:**
```bash
# Generate encryption secret
openssl rand -base64 32

# Generate session secret
openssl rand -hex 32
```

Edit `.env` and set your values:

```env
ENCRYPTION_SECRET=your-generated-encryption-secret
SESSION_SECRET=your-generated-session-secret
BACKEND_URL=http://localhost:8080
FRONTEND_URL=http://localhost:8080
```

**Important:** Always set custom `ENCRYPTION_SECRET` and `SESSION_SECRET` in production!

### 3. Configure Customers

```bash
cp config/customers.json.example config/customers.json
```

Edit `config/customers.json` with your actual customer data:

```json
{
  "customers": [
    {
      "id": "bcv",
      "name": "BCV",
      "repo_url": "https://code.swisscom.com/your-group/bcv-kpt-sif.git",
      "stages": ["dev", "tst", "prd"]
    }
  ]
}
```

### 4. Run with Docker Compose

```bash
docker-compose up -d
```

The application will be available at `http://localhost:8080`

### 5. Initial Setup

1. **Login** with default credentials:
   - Username: `admin`
   - Password: `admin`

2. **Change Admin Password** (Important!):
   - Go to "Users" in the header
   - Change the admin password immediately

3. **Configure GitLab Token** (Admin only):
   - Click "Settings" in the header
   - Enter your GitLab Group Access Token
   - Save configuration

4. **Configure Customers** (Admin only):
   - Click "Customers" in the header
   - Add/edit customer repositories and stages

5. **Create Users** (Admin only):
   - Click "Users" in the header
   - Add team members who need access

## Development Setup

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Set environment variables before running:
```bash
export ENCRYPTION_SECRET=$(openssl rand -base64 32)
export SESSION_SECRET=$(openssl rand -hex 32)
export BACKEND_URL=http://localhost:8000
export FRONTEND_URL=http://localhost:3000
export CONFIG_FILE=../config/customers.json
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

The development server will run at `http://localhost:3000` with proxy to backend.

### Testing Changes

#### Backend Testing

```bash
cd backend
source venv/bin/activate
python -m pytest  # If tests exist
```

#### Frontend Testing

```bash
cd frontend
npm run build  # Ensure build succeeds
npm run lint   # Check for linting errors
```

## Contributing

### Development Workflow

1. **Clone the repository**
2. **Set up environment** (see Development Setup above)
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Making Changes

#### Backend Changes

- Code is in `backend/app/`
- Follow PEP 8 style guidelines
- Add type hints to functions
- Update `requirements.txt` if adding dependencies

Example:
```python
def parse_service_url(url: str) -> tuple[str, str]:
    """
    Parse service URL to extract name and version.

    Args:
        url: Full service URL

    Returns:
        Tuple of (service_name, version)
    """
    # Implementation
    pass
```

#### Frontend Changes

- Code is in `frontend/src/`
- Follow TypeScript best practices
- Use functional components with hooks
- Update `package.json` if adding dependencies

Example:
```typescript
interface ServiceProps {
  name: string;
  version: string;
}

export default function Service({ name, version }: ServiceProps) {
  return <div>{name} - {version}</div>;
}
```

### Code Style

#### Python (Backend)

- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use meaningful variable names
- Add docstrings to functions
- Use type hints

#### TypeScript (Frontend)

- Use 2 spaces for indentation
- Use functional components
- Use hooks for state management
- Export default for components
- Use interfaces for types

### Project Structure

```
fil-deployer/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── main.py      # FastAPI app entry point
│   │   ├── auth.py      # Authentication routes
│   │   ├── config.py    # Configuration management
│   │   ├── app_config.py     # App configuration with encryption
│   │   ├── crypto_utils.py   # Encryption/decryption logic
│   │   ├── gitlab_client.py  # GitLab API client
│   │   ├── csv_handler.py    # CSV parsing logic
│   │   └── models.py    # Pydantic models
│   └── requirements.txt
├── frontend/            # React TypeScript frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API client
│   │   ├── App.tsx      # Main app component
│   │   └── main.tsx     # Entry point
│   └── package.json
├── config/              # Configuration files
│   ├── customers.json   # Customer/repo configuration
│   ├── app_config.json  # App config (tokens encrypted)
│   └── users.json       # User database
├── Dockerfile           # Multi-stage Docker build
├── docker-compose.yml   # Docker Compose config
└── README.md            # This file
```

### Adding Features

#### Adding a New API Endpoint

1. Define Pydantic model in `backend/app/models.py`
2. Add route in `backend/app/main.py` or create new router
3. Add authentication dependency if needed
4. Update frontend API client in `frontend/src/services/api.ts`
5. Update TypeScript types in `frontend/src/types.ts`

#### Adding a New UI Component

1. Create component in `frontend/src/components/`
2. Create corresponding CSS file
3. Import and use in parent component
4. Add to `App.tsx` if it's a new page/section

#### Modifying CSV Handler

1. Update parsing logic in `backend/app/csv_handler.py`
2. Add tests for new patterns
3. Update documentation if format changes

### Committing Changes

1. **Stage your changes**:
   ```bash
   git add .
   ```

2. **Commit with descriptive message**:
   ```bash
   git commit -m "Add feature: description of changes"
   ```

3. **Push to remote**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create merge request** in GitLab

## Usage

### 1. Login

Enter your username and password (default: admin/admin).

### 2. First-Time Setup (Admin only)

After first login:
1. Go to **Users** → Change admin password
2. Go to **Settings** → Configure GitLab Group Access Token
3. Go to **Customers** → Configure customer repositories
4. Go to **Users** → Add team members

### 3. Select Customer and Stage

Use the dropdown menus to select:
- Customer (e.g., BCV)
- Stage (e.g., dev, tst, prd)

### 4. Edit Services

The application will load the services.csv file and display services in a simplified format:
- Service Name: `realEstateAdministration`
- Version: `7.0.1`

You can:
- Edit existing services
- Add new services with the "+ Add Service" button
- Remove services with the "Remove" button

### 5. Save and Create Merge Request

Click "Save & Create MR" to:
1. Create a feature branch: `fil-deploy/{username}/{timestamp}`
2. Commit changes to services.csv with message: "Update services.csv for {stage} by {username}"
3. Push the branch
4. Create a merge request automatically

The application will display a success message with a link to the merge request.

### 6. Admin Features

Admins have access to:
- **Settings**: Configure GitLab URL and Group Access Token
- **Users**: Create, view, and delete users
- **Customers**: Manage customer/repository mappings

## How It Works

### Service URL Format

Services are stored in the repository as full URLs:
```
https://bin.swisscom.com/artifactory/omega-fils-generic-local/gitlab/fil/realEstateAdministration/realEstateAdministration-7.0.1.tgz
```

The application extracts and displays them as:
- **Name**: `realEstateAdministration`
- **Version**: `7.0.1`

When saving, it normalizes them back to full URLs based on naming patterns:
- `bsa-*` services → `bsa-camel3` group
- All others → `fil` group

### Git Operations

1. Uses the configured Group Access Token for all Git operations
2. Clones/updates the repository
3. Creates a feature branch from main/master: `fil-deploy/{username}/{timestamp}`
4. Modifies the services.csv file at: `{stage}/9620/sif/instance/stage/sif-services-pipeline/instance/config/services.csv`
5. Commits with message: "Update services.csv for {stage} by {username}"
6. Pushes the branch
7. Creates a merge request via GitLab API

## User Management

### Default Admin Account

- **Username**: `admin`
- **Password**: `admin`
- **⚠️ Change the password after first login!**

### Creating New Users

1. Login as admin
2. Click "Users" in the header
3. Click "+ Add User"
4. Fill in user details (username, password, full name, email)
5. Optionally grant admin privileges
6. Click "Create User"

### User Roles

- **Admin**: Can manage users, customers, and GitLab tokens
- **User**: Can deploy services to configured customers/stages

## Configuration Management

### GitLab Token

Configure the Group Access Token via the UI:
1. Login as admin
2. Click "Settings"
3. Enter GitLab URL and Group Access Token
4. Click "Save Configuration"

The token is automatically encrypted when saved to `config/app_config.json`.

### Customer Repositories

Manage customers via the UI:
1. Login as admin
2. Click "Customers"
3. Add/edit/remove customer configurations
4. Click "Save Configuration"

Or edit `config/customers.json` directly.

## Security

### Token Encryption

#### Overview

Sensitive data (GitLab and Artifactory tokens) in `config/app_config.json` are automatically encrypted at rest using **Fernet symmetric encryption** from the `cryptography` library.

#### How It Works

1. **Encryption Algorithm**: Fernet (AES-128-CBC with HMAC authentication)
2. **Key Derivation**: PBKDF2-HMAC-SHA256 with 100,000 iterations
3. **Automatic Encryption**: Tokens are encrypted when saved, decrypted when loaded
4. **Backward Compatible**: Existing plaintext tokens are automatically encrypted on first save

#### Architecture

```
┌─────────────────────┐
│  User enters token  │
│   via Settings UI   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   API receives      │
│   plaintext token   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────┐
│  app_config.py              │
│  ├─ Encrypts with Fernet    │
│  └─ Saves to JSON           │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  config/app_config.json     │
│  {                          │
│    "gitlab_group_token":    │
│      "gAAAAABl..."          │  ← Encrypted!
│  }                          │
└──────────┬──────────────────┘
           │
           ▼ (on read)
┌─────────────────────────────┐
│  app_config.py              │
│  ├─ Loads from JSON         │
│  ├─ Detects encrypted token │
│  └─ Decrypts with Fernet    │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────┐
│  Application uses   │
│  decrypted token    │
└─────────────────────┘
```

#### Encryption Key Configuration

The encryption key is derived from a secret using PBKDF2:

```python
Secret → PBKDF2-HMAC-SHA256 (100k iterations) → Fernet Key
```

**Set via Environment Variable (Recommended for Production):**
```bash
# Generate a strong secret
export ENCRYPTION_SECRET=$(openssl rand -base64 32)

# Or in .env file
echo "ENCRYPTION_SECRET=$(openssl rand -base64 32)" >> .env
```

**Docker Compose:**
```yaml
environment:
  - ENCRYPTION_SECRET=${ENCRYPTION_SECRET}
```

#### Fallback Behavior

If `ENCRYPTION_SECRET` is not set, the application will:
1. ⚠️  Display a warning in logs
2. Use a default secret (not recommended for production)

**Always set a custom `ENCRYPTION_SECRET` in production!**

#### Key Rotation

To rotate encryption keys:

1. **Export existing tokens** (they're encrypted with old key)
2. **Set new `ENCRYPTION_SECRET`**
3. **Re-enter tokens** via Settings UI (will encrypt with new key)
4. **Restart application**

⚠️ **Warning:** Changing `ENCRYPTION_SECRET` will make existing encrypted tokens unreadable!

#### Security Benefits

✅ **At-Rest Protection**: Tokens are encrypted in the file system
✅ **Automatic**: No manual encryption needed
✅ **Transparent**: Application code doesn't change
✅ **HMAC Authentication**: Prevents tampering
✅ **Standard Algorithm**: Uses industry-standard Fernet

#### Limitations

⚠️ **Not End-to-End**: Tokens are decrypted in application memory
⚠️ **Single Key**: All tokens use the same encryption key
⚠️ **Key Rotation**: Changing encryption key requires re-entering all tokens

### Authentication

- Session-based authentication with secure cookies
- Password hashing with secure algorithms
- Admin-only access to sensitive operations

### CORS

- Restricted to configured frontend URL
- Credentials support enabled
- Prevents unauthorized cross-origin requests

### Input Validation

- Pydantic models validate all API inputs
- CSV parsing with error handling
- GitLab/Artifactory API validation

### Security Best Practices

For production deployment:

1. **✅ Set `ENCRYPTION_SECRET`**: Always use a custom encryption secret
   ```bash
   export ENCRYPTION_SECRET=$(openssl rand -base64 32)
   ```

2. **✅ Set `SESSION_SECRET`**: Use a strong session secret
   ```bash
   export SESSION_SECRET=$(openssl rand -hex 32)
   ```

3. **🔒 Keep Secrets Secure**: Never commit `.env` file to git
   ```bash
   echo ".env" >> .gitignore
   ```

4. **🔄 Rotate Keys Periodically**: Implement key rotation strategy
   - Backup existing tokens before rotation
   - Set new `ENCRYPTION_SECRET`
   - Re-enter all tokens via UI

5. **📁 Access Control**: Restrict file system access to `config/` directory
   ```bash
   chmod 600 config/app_config.json
   chmod 600 config/users.json
   chmod 600 .env
   ```

6. **🔐 Secrets Management**: For enterprise deployments, consider:
   - HashiCorp Vault
   - AWS Secrets Manager
   - Azure Key Vault
   - Google Cloud Secret Manager

7. **⚠️ Change Default Password**: Change admin password immediately after first login

8. **🔒 Use HTTPS**: Always use HTTPS in production

9. **🔑 Rotate Tokens**: Rotate GitLab access tokens regularly

10. **👥 Audit Users**: Regularly audit user accounts and permissions

### GitLab API Integration

When working with GitLab API:
- Use `python-gitlab` library
- Handle rate limits
- Add error handling
- Log API calls for debugging
- Never log sensitive data (tokens, passwords)

Example:
```python
try:
    project = self.gl.projects.get(project_id)
except gitlab.GitlabGetError as e:
    logger.error(f"Failed to get project: {e}")
    raise HTTPException(status_code=404, detail="Project not found")
```

## Deployment

### Docker Deployment

#### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

#### Quick Deploy

1. **Set environment variables**
   ```bash
   # Create .env file
   cat > .env << 'EOF'
   ENCRYPTION_SECRET=$(openssl rand -base64 32)
   SESSION_SECRET=$(openssl rand -base64 32)
   EOF
   ```

2. **Build and run**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Application: http://localhost:8080
   - Default credentials: admin / admin

4. **View logs**
   ```bash
   docker-compose logs -f
   ```

5. **Stop the application**
   ```bash
   docker-compose down
   ```

### Production Deployment

#### Security Checklist

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

- [ ] **Configure Artifactory token** via Settings UI (if needed)

- [ ] **Restrict file permissions**
  ```bash
  chmod 600 config/app_config.json
  chmod 600 config/users.json
  chmod 600 .env
  ```

- [ ] **Enable HTTPS** (reverse proxy recommended)

- [ ] **Set up backup** for config/ directory

#### Environment Variables

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

#### Docker Production Configuration

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

#### Reverse Proxy (nginx)

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

### Backup and Recovery

#### Backup

Backup the following directories:

```bash
# Create backup
tar -czf fil-deployer-backup-$(date +%Y%m%d).tar.gz \
  config/ \
  .env

# Store securely (encrypted recommended)
gpg -c fil-deployer-backup-$(date +%Y%m%d).tar.gz
```

#### Recovery

```bash
# Extract backup
tar -xzf fil-deployer-backup-20240101.tar.gz

# Restore config
cp -r config/ /path/to/fil_deployer/
cp .env /path/to/fil_deployer/

# Restart application
docker-compose restart
```

### Monitoring

#### Health Checks

```bash
# Backend API health
curl http://localhost:8000/

# Check logs
docker-compose logs -f fil-deployer
```

#### Log Files

Logs are output to stdout/stderr. View with:

```bash
docker-compose logs --tail=100 -f
```

### Updating

#### Update Application

```bash
# Pull latest changes
git pull

# Rebuild Docker image
docker-compose down
docker-compose build
docker-compose up -d
```

#### Database Migrations

Currently using JSON files (no migrations needed).
Config files are automatically migrated on startup.

## Troubleshooting

### Login Failed

- Default credentials are `admin` / `admin`
- Check browser console for errors
- Ensure backend is running on port 8000

### GitLab Token Not Configured

If you see "GitLab token not configured":
1. Login as admin
2. Go to Settings
3. Configure the Group Access Token

### Repository Access Issues

Verify the group access token has:
- `api` scope
- `write_repository` scope
- Access to all customer repositories (group-level token recommended)

### Services Not Loading

Check:
1. Repository URL is correct in `customers.json`
2. Stage exists in the repository
3. Path to services.csv follows the expected pattern
4. Group access token has read permissions

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

## Support

For issues or questions, contact the development team or open an issue in GitLab.

## License

Internal Swisscom project.
