# Detailed Setup Guide

This guide provides detailed instructions for setting up the FIL Deployer application.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [GitLab Configuration](#gitlab-configuration)
3. [Application Configuration](#application-configuration)
4. [Development Setup](#development-setup)
5. [Production Deployment](#production-deployment)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Docker**: Version 20.0 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: For cloning the repository

### For Development

- **Python**: Version 3.11 or higher
- **Node.js**: Version 18 or higher
- **npm**: Version 9 or higher

### GitLab Requirements

- Access to code.swisscom.com
- Admin access to create OAuth applications
- Group maintainer access to create access tokens
- Access to customer repositories

## GitLab Configuration

### Step 1: Create OAuth Application

1. Navigate to `https://code.swisscom.com/-/profile/applications`
2. Click "Add new application"
3. Fill in the details:
   - **Name**: FIL Deployer
   - **Redirect URI**: 
     - Development: `http://localhost:8080/auth/callback`
     - Production: `https://your-domain.com/auth/callback`
   - **Confidential**: Yes
   - **Scopes**: 
     - ✓ `read_user`
     - ✓ `api`
4. Click "Save application"
5. **Important**: Copy the Application ID and Secret immediately

### Step 2: Create Group Access Token

1. Navigate to your group in GitLab
2. Go to Settings → Access Tokens
3. Create a new token:
   - **Name**: FIL Deployer Service
   - **Role**: Maintainer
   - **Scopes**:
     - ✓ `api`
     - ✓ `write_repository`
4. Click "Create group access token"
5. **Important**: Copy the token immediately (it won't be shown again)

### Step 3: Verify Repository Access

Ensure the group access token has access to all customer repositories:

```bash
curl -H "PRIVATE-TOKEN: your_token" \
  https://code.swisscom.com/api/v4/projects?membership=true
```

## Application Configuration

### Step 1: Environment Variables

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# GitLab OAuth Configuration
GITLAB_URL=https://code.swisscom.com
GITLAB_CLIENT_ID=<your_oauth_application_id>
GITLAB_CLIENT_SECRET=<your_oauth_secret>

# GitLab Group Access Token
GITLAB_GROUP_TOKEN=<your_group_access_token>

# Session Secret - Generate with: openssl rand -hex 32
SESSION_SECRET=<generate_random_string>

# Application URLs
BACKEND_URL=http://localhost:8080
FRONTEND_URL=http://localhost:8080

# Configuration
CONFIG_FILE=/app/config/customers.json
GIT_CACHE_DIR=/tmp/fil-deployer-repos
```

**Generate a secure session secret:**

```bash
openssl rand -hex 32
```

### Step 2: Customer Configuration

Create `config/customers.json`:

```bash
cp config/customers.json.example config/customers.json
```

Edit with your customer data:

```json
{
  "customers": [
    {
      "id": "bcv",
      "name": "BCV Bank",
      "repo_url": "https://code.swisscom.com/fop/bcv-kpt-sif.git",
      "stages": ["dev", "tst", "prd"]
    }
  ]
}
```

**Configuration Fields:**

- `id`: Short identifier (used in URLs, lowercase, no spaces)
- `name`: Display name shown in UI
- `repo_url`: Full GitLab repository URL (must end with .git)
- `stages`: Array of stage names available for this customer

### Step 3: Verify Configuration

Verify your configuration is valid:

```bash
# Test GitLab connectivity
curl -H "PRIVATE-TOKEN: your_group_token" \
  https://code.swisscom.com/api/v4/user

# Test repository access
curl -H "PRIVATE-TOKEN: your_group_token" \
  https://code.swisscom.com/api/v4/projects/your-project-id
```

## Development Setup

### Backend Setup

1. **Create virtual environment:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Set environment variables:**

```bash
export GITLAB_URL=https://code.swisscom.com
export GITLAB_CLIENT_ID=your_client_id
export GITLAB_CLIENT_SECRET=your_client_secret
export GITLAB_GROUP_TOKEN=your_group_token
export SESSION_SECRET=your_secret
export BACKEND_URL=http://localhost:8000
export FRONTEND_URL=http://localhost:3000
export CONFIG_FILE=../config/customers.json
```

Or create a `.env` file and use `python-dotenv`.

4. **Run the backend:**

```bash
uvicorn app.main:app --reload --port 8000
```

Backend will run at `http://localhost:8000`

### Frontend Setup

1. **Install dependencies:**

```bash
cd frontend
npm install
```

2. **Run development server:**

```bash
npm run dev
```

Frontend will run at `http://localhost:3000` with proxy to backend.

### Testing the Setup

1. Open `http://localhost:3000` in your browser
2. Click "Login with GitLab"
3. Authenticate with your GitLab account
4. You should be redirected back to the application
5. Select a customer and stage
6. Services should load from the repository

## Production Deployment

### Step 1: Prepare Environment

1. **Update `.env` for production:**

```env
GITLAB_URL=https://code.swisscom.com
GITLAB_CLIENT_ID=<production_oauth_id>
GITLAB_CLIENT_SECRET=<production_oauth_secret>
GITLAB_GROUP_TOKEN=<production_group_token>
SESSION_SECRET=<strong_random_secret>
BACKEND_URL=https://fil-deployer.your-domain.com
FRONTEND_URL=https://fil-deployer.your-domain.com
```

2. **Update GitLab OAuth redirect URI:**

Go to GitLab OAuth application settings and update redirect URI to:
```
https://fil-deployer.your-domain.com/auth/callback
```

### Step 2: Build Docker Image

```bash
docker-compose build
```

### Step 3: Start the Application

```bash
docker-compose up -d
```

### Step 4: Verify Deployment

```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs -f

# Test health endpoint
curl http://localhost:8080/
```

### Step 5: Configure Reverse Proxy (Optional)

If using nginx as a reverse proxy:

```nginx
server {
    listen 443 ssl;
    server_name fil-deployer.your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Troubleshooting

### Authentication Issues

**Problem**: OAuth callback fails

**Solution**: 
- Verify redirect URI matches exactly in GitLab OAuth settings
- Check `BACKEND_URL` in `.env` matches your domain
- Ensure no trailing slashes in URLs

**Problem**: "Not authenticated" errors

**Solution**:
- Check session secret is set and consistent
- Verify cookies are enabled in browser
- Check browser console for CORS errors

### Repository Access Issues

**Problem**: "Error loading services"

**Solution**:
- Verify repository URL in `customers.json` is correct
- Ensure group access token has read access to repository
- Check stage name matches directory in repository
- Verify path: `{stage}/9620/sif/instance/stage/sif-services-pipeline/instance/config/services.csv`

**Problem**: "Failed to create merge request"

**Solution**:
- Verify group access token has `api` and `write_repository` scopes
- Ensure user has merge request permissions on repository
- Check GitLab API logs for specific errors

### Docker Issues

**Problem**: Container won't start

**Solution**:
```bash
# Check logs
docker-compose logs

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Problem**: Out of disk space

**Solution**:
```bash
# Clean up Docker resources
docker system prune -a

# Remove old volumes
docker volume prune
```

### Performance Issues

**Problem**: Slow service loading

**Solution**:
- Git repositories are cached in `/tmp/fil-deployer-repos`
- First load will be slower (cloning)
- Subsequent loads should be faster (git fetch only)
- Consider using a persistent volume for git cache in production

### Development Issues

**Problem**: Backend/Frontend connection fails

**Solution**:
- Verify backend is running on port 8000
- Verify frontend proxy configuration in `vite.config.ts`
- Check CORS settings in backend `main.py`

## Maintenance

### Regular Tasks

1. **Rotate Access Tokens** (every 90 days):
   - Create new group access token
   - Update `.env` file
   - Restart application

2. **Update Dependencies**:
   ```bash
   # Backend
   cd backend
   pip install --upgrade -r requirements.txt
   
   # Frontend
   cd frontend
   npm update
   ```

3. **Clean Git Cache**:
   ```bash
   # In production
   docker-compose exec fil-deployer rm -rf /tmp/fil-deployer-repos/*
   
   # In development
   rm -rf /tmp/fil-deployer-repos/*
   ```

4. **Monitor Logs**:
   ```bash
   docker-compose logs -f --tail=100
   ```

### Backup

Important files to backup:
- `config/customers.json` - Customer configuration
- `.env` - Environment variables (store securely)

### Updates

To update the application:

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

## Security Best Practices

1. **Never commit sensitive data**:
   - `.env` file
   - Access tokens
   - Customer configurations with sensitive data

2. **Rotate credentials regularly**:
   - Group access token (every 90 days)
   - Session secret (every 6 months)
   - OAuth application credentials (yearly)

3. **Use HTTPS in production**:
   - All traffic should be encrypted
   - Enable HSTS headers

4. **Restrict access**:
   - Limit who can create OAuth applications
   - Restrict group access token permissions
   - Use VPN or IP allowlisting if possible

5. **Monitor activity**:
   - Review merge requests
   - Monitor GitLab audit logs
   - Check application logs regularly

## Support

For additional help:
1. Check application logs
2. Review GitLab API documentation
3. Contact the development team

