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

## Architecture

- **Backend**: Python FastAPI with GitLab API integration
- **Frontend**: React with TypeScript
- **Deployment**: Docker container with Nginx reverse proxy
- **Authentication**: Simple username/password with session management
- **User Storage**: JSON-based user database

## Prerequisites

- Docker and Docker Compose
- GitLab group access token with API and write_repository permissions

## Quick Start

### 1. Clone the Repository

```bash
cd /path/to/fil_deployer
```

### 2. Create Environment File (Optional)

```bash
cp .env.example .env
```

You can use the default settings or customize:

```env
SESSION_SECRET=change_me_in_production
BACKEND_URL=http://localhost:8080
FRONTEND_URL=http://localhost:8080
```

Note: GitLab token is configured via the UI after first login.

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

2. **Configure GitLab Token** (Admin only):
   - Click "Settings" in the header
   - Enter your GitLab Group Access Token
   - Save configuration

3. **Configure Customers** (Admin only):
   - Click "Customers" in the header
   - Add/edit customer repositories and stages

4. **Create Users** (Admin only):
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
export SESSION_SECRET=dev_secret
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

## Usage

### 1. Login

Enter your username and password (default: admin/admin).

### 2. First-Time Setup (Admin only)

After first login:
1. Go to **Settings** → Configure GitLab Group Access Token
2. Go to **Customers** → Configure customer repositories
3. Go to **Users** → Add team members

### 3. Select Customer and Stage

Use the dropdown menus to select:
- Customer (e.g., BCV)
- Stage (e.g., dev, tst, prd)

### 3. Edit Services

The application will load the services.csv file and display services in a simplified format:
- Service Name: `realEstateAdministration`
- Version: `7.0.1`

You can:
- Edit existing services
- Add new services with the "+ Add Service" button
- Remove services with the "Remove" button

### 4. Save and Create Merge Request

Click "Save & Create MR" to:
1. Create a feature branch: `fil-deploy/{username}/{timestamp}`
2. Commit changes to services.csv with message: "Update services.csv for {stage} by {username}"
3. Push the branch
4. Create a merge request automatically

The application will display a success message with a link to the merge request.

### 5. Admin Features

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
- **Change the password after first login!**

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

### Customer Repositories

Manage customers via the UI:
1. Login as admin
2. Click "Customers"
3. Add/edit/remove customer configurations
4. Click "Save Configuration"

Or edit `config/customers.json` directly.

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

## Production Deployment

### Update Environment Variables

For production, update `.env` with:
```env
SESSION_SECRET=strong_random_secret_generate_with_openssl
BACKEND_URL=https://your-domain.com
FRONTEND_URL=https://your-domain.com
```

Generate a secure session secret:
```bash
openssl rand -hex 32
```

### Build and Deploy

```bash
docker-compose build
docker-compose up -d
```

### Reverse Proxy (Optional)

If running behind a reverse proxy, ensure it forwards:
- Host header
- X-Real-IP
- X-Forwarded-For
- X-Forwarded-Proto

## Security Considerations

- **Change default admin password immediately after first login**
- Store `.env` file securely, never commit to git
- Use strong, random `SESSION_SECRET` in production
- Use strong passwords for all users
- Rotate GitLab access tokens regularly
- Use HTTPS in production
- Restrict group access token permissions to minimum required
- Review merge requests before merging to production
- Only grant admin privileges to trusted users
- Regularly audit user accounts

## Support

For issues or questions, contact the development team.

## License

Internal Swisscom project.

