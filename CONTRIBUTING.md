# Contributing to FIL Deployer

## Development Workflow

### Getting Started

1. **Clone the repository**
2. **Set up environment** (see README.md)
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

#### Frontend Changes

- Code is in `frontend/src/`
- Follow TypeScript best practices
- Use functional components with hooks
- Update `package.json` if adding dependencies

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

## Code Style

### Python (Backend)

- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use meaningful variable names
- Add docstrings to functions
- Use type hints

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

### TypeScript (Frontend)

- Use 2 spaces for indentation
- Use functional components
- Use hooks for state management
- Export default for components
- Use interfaces for types

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

## Project Structure

```
fil-deployer/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── main.py      # FastAPI app entry point
│   │   ├── auth.py      # Authentication routes
│   │   ├── config.py    # Configuration management
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
├── config/              # Customer configuration
│   └── customers.json
├── docs/                # Documentation
├── Dockerfile           # Multi-stage Docker build
├── docker-compose.yml   # Docker Compose config
└── README.md            # Main documentation
```

## Adding Features

### Adding a New API Endpoint

1. Define Pydantic model in `backend/app/models.py`
2. Add route in `backend/app/main.py` or create new router
3. Add authentication dependency if needed
4. Update frontend API client in `frontend/src/services/api.ts`
5. Update TypeScript types in `frontend/src/types.ts`

### Adding a New UI Component

1. Create component in `frontend/src/components/`
2. Create corresponding CSS file
3. Import and use in parent component
4. Add to `App.tsx` if it's a new page/section

### Modifying CSV Handler

1. Update parsing logic in `backend/app/csv_handler.py`
2. Add tests for new patterns
3. Update documentation if format changes

## Common Tasks

### Add a New Customer

Customers can be added via:
1. **UI**: Use the Config Panel (Show Config button)
2. **Manually**: Edit `config/customers.json`

### Update Dependencies

Backend:
```bash
pip install <package>
pip freeze > requirements.txt
```

Frontend:
```bash
npm install <package>
```

### Debug Issues

Backend:
```bash
# Enable debug logging
uvicorn app.main:app --reload --log-level debug
```

Frontend:
```bash
# Check browser console
# Use React DevTools
```

## GitLab API Integration

When working with GitLab API:
- Use `python-gitlab` library
- Handle rate limits
- Add error handling
- Log API calls for debugging

Example:
```python
try:
    project = self.gl.projects.get(project_id)
except gitlab.GitlabGetError as e:
    logger.error(f"Failed to get project: {e}")
    raise HTTPException(status_code=404, detail="Project not found")
```

## Security Considerations

- Never log sensitive data (tokens, passwords)
- Validate all user input
- Use parameterized queries
- Sanitize file paths
- Check permissions before operations

## Questions?

Contact the development team or create an issue in GitLab.

