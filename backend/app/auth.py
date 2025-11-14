from fastapi import APIRouter, Request, HTTPException, Depends
from .models import UserInfo, LoginRequest
from .user_storage import user_storage


router = APIRouter()


def get_current_user(request: Request) -> UserInfo:
    """Dependency to get current authenticated user"""
    user_data = request.session.get('user')
    if not user_data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return UserInfo(**user_data)


def require_admin(current_user: UserInfo = Depends(get_current_user)) -> UserInfo:
    """Dependency to require admin privileges"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user


@router.post("/login")
async def login(request: Request, login_data: LoginRequest):
    """Login with username and password"""
    user = user_storage.authenticate(login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Store in session
    request.session['user'] = user.dict()
    
    return user


@router.get("/user")
async def get_user(current_user: UserInfo = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.post("/logout")
async def logout(request: Request):
    """Logout user"""
    request.session.clear()
    return {"success": True}

