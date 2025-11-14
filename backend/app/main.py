from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from typing import List
from .config import config
from .models import (
    Customer, Service, ServiceUpdate, SaveServicesRequest, 
    SaveServicesResponse, UserInfo, UserCreate, AppConfig
)
from .csv_handler import CSVHandler
from .gitlab_client import GitLabClient
from .auth import router as auth_router, get_current_user, require_admin
from .user_storage import user_storage
from .app_config import app_config_manager


app = FastAPI(title="FIL Deployer API")

# Add session middleware
app.add_middleware(
    SessionMiddleware, 
    secret_key=config.session_secret,
    max_age=86400  # 24 hours
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth router
app.include_router(auth_router, prefix="/auth", tags=["auth"])


@app.get("/")
async def root():
    """API health check"""
    return {"status": "ok", "service": "FIL Deployer API"}


@app.get("/api/customers", response_model=List[Customer])
async def get_customers(current_user: UserInfo = Depends(get_current_user)):
    """Get list of all customers"""
    return config.load_customers()


@app.get("/api/customers/{customer_id}/stages", response_model=List[str])
async def get_customer_stages(
    customer_id: str,
    current_user: UserInfo = Depends(get_current_user)
):
    """Get stages for a specific customer"""
    customer = config.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer.stages


@app.get("/api/services/{customer_id}/{stage}", response_model=List[Service])
async def get_services(
    customer_id: str,
    stage: str,
    current_user: UserInfo = Depends(get_current_user)
):
    """Get services for a customer and stage"""
    customer = config.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if stage not in customer.stages:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    # Get GitLab token from app config
    gitlab_token = app_config_manager.get_gitlab_token()
    if not gitlab_token:
        raise HTTPException(status_code=500, detail="GitLab token not configured")
    
    gitlab_url = app_config_manager.get_gitlab_url()
    
    # Initialize GitLab client
    gitlab_client = GitLabClient(group_token=gitlab_token, gitlab_url=gitlab_url)
    
    try:
        # Read services.csv
        csv_content = gitlab_client.read_services_csv(
            customer.repo_url, 
            stage,
            customer.csv_path_template
        )
        
        # Parse CSV
        services = CSVHandler.parse_csv(csv_content)
        
        return services
    except FileNotFoundError as e:
        import traceback
        print(f"FileNotFoundError for {customer_id}/{stage}: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import traceback
        print(f"Error reading services for {customer_id}/{stage}: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error reading services: {str(e)}")


@app.post("/api/services/validate", response_model=dict)
async def validate_service(
    request: ServiceUpdate,
    current_user: UserInfo = Depends(get_current_user)
):
    """Validate a single service against Artifactory"""
    try:
        artifactory_token = app_config_manager.get_artifactory_token()
        errors = CSVHandler.validate_services([request], artifactory_token)
        
        return {
            "valid": len(errors) == 0,
            "error": errors[0] if errors else None
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"Validation error: {str(e)}"
        }


@app.post("/api/services/{customer_id}/{stage}", response_model=SaveServicesResponse)
async def save_services(
    customer_id: str,
    stage: str,
    request: SaveServicesRequest,
    current_user: UserInfo = Depends(get_current_user)
):
    """Save services and create merge request"""
    customer = config.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if stage not in customer.stages:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    # Get GitLab token from app config
    gitlab_token = app_config_manager.get_gitlab_token()
    if not gitlab_token:
        raise HTTPException(status_code=500, detail="GitLab token not configured")
    
    gitlab_url = app_config_manager.get_gitlab_url()
    
    # Initialize GitLab client
    gitlab_client = GitLabClient(group_token=gitlab_token, gitlab_url=gitlab_url)
    
    try:
        # Get Artifactory token from app config
        artifactory_token = app_config_manager.get_artifactory_token()
        
        # Validate all services exist in Artifactory
        validation_errors = CSVHandler.validate_services(request.services, artifactory_token)
        
        if validation_errors:
            # Return validation errors to user
            error_detail = "Service validation failed:\n" + "\n".join(f"• {err}" for err in validation_errors)
            raise HTTPException(
                status_code=400,
                detail=error_detail
            )
        
        # Generate new CSV content
        csv_content = CSVHandler.generate_csv(request.services, artifactory_token)
        
        # Save and create MR (with username, optional Jira ticket and message)
        mr_url = gitlab_client.save_services_csv(
            customer.repo_url,
            stage,
            csv_content,
            current_user.username,
            customer.csv_path_template,
            request.jira_ticket,
            request.message
        )
        
        return SaveServicesResponse(
            success=True,
            message=f"Successfully created merge request for {stage}",
            merge_request_url=mr_url
        )
    except HTTPException:
        # Re-raise HTTP exceptions (including validation errors)
        raise
    except Exception as e:
        import traceback
        print(f"Error saving services for {customer_id}/{stage}: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500, 
            detail=f"Error saving services: {str(e)}"
        )


@app.get("/api/config", response_model=List[Customer])
async def get_config(current_user: UserInfo = Depends(get_current_user)):
    """Get customer configuration (admin)"""
    return config.load_customers()


@app.put("/api/config")
async def update_config(
    customers: List[Customer],
    current_user: UserInfo = Depends(require_admin)
):
    """Update customer configuration (admin only)"""
    try:
        config.save_customers(customers)
        return {"success": True, "message": "Configuration updated"}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error updating configuration: {str(e)}"
        )


# User Management Endpoints
@app.get("/api/users", response_model=List[UserInfo])
async def list_users(admin_user: UserInfo = Depends(require_admin)):
    """List all users (admin only)"""
    return user_storage.list_users()


@app.post("/api/users", response_model=UserInfo)
async def create_user(
    user_data: UserCreate,
    admin_user: UserInfo = Depends(require_admin)
):
    """Create a new user (admin only)"""
    try:
        return user_storage.create_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/users/{username}")
async def update_user(
    username: str,
    updates: dict,
    admin_user: UserInfo = Depends(require_admin)
):
    """Update user (admin only)"""
    user = user_storage.update_user(username, updates)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.delete("/api/users/{username}")
async def delete_user(
    username: str,
    admin_user: UserInfo = Depends(require_admin)
):
    """Delete user (admin only)"""
    if username == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete admin user")
    
    if user_storage.delete_user(username):
        return {"success": True, "message": "User deleted"}
    raise HTTPException(status_code=404, detail="User not found")


# App Configuration Endpoints
@app.get("/api/app-config")
async def get_app_config(admin_user: UserInfo = Depends(require_admin)):
    """Get app configuration (admin only, token masked)"""
    return app_config_manager.get_all_config()


@app.put("/api/app-config")
async def update_app_config(
    app_config: AppConfig,
    admin_user: UserInfo = Depends(require_admin)
):
    """Update app configuration (admin only)"""
    try:
        token_changed = False
        
        # Only update if token is provided and not masked
        if app_config.gitlab_group_token and not app_config.gitlab_group_token.startswith('•'):
            app_config_manager.set_gitlab_token(app_config.gitlab_group_token)
            token_changed = True
            
        if app_config.gitlab_url:
            app_config_manager.set_gitlab_url(app_config.gitlab_url)
            
        if app_config.artifactory_token and not app_config.artifactory_token.startswith('•'):
            app_config_manager.set_artifactory_token(app_config.artifactory_token)
            
        if app_config.artifactory_url:
            app_config_manager.set_artifactory_url(app_config.artifactory_url)
        
        # If GitLab token changed, clear repo cache to force re-clone with new token
        if token_changed:
            import shutil
            import os
            repos_dir = "/tmp/fil-deployer-repos"
            if os.path.exists(repos_dir):
                for item in os.listdir(repos_dir):
                    item_path = os.path.join(repos_dir, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                print("GitLab token updated - cleared all repository caches")
            
        return {"success": True, "message": "Configuration updated"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating configuration: {str(e)}"
        )

