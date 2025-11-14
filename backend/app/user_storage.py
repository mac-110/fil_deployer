import json
import hashlib
from pathlib import Path
from typing import List, Optional
from .models import User, UserCreate, UserInfo


class UserStorage:
    """Simple JSON-based user storage"""
    
    def __init__(self, storage_file: str = "config/users.json"):
        self.storage_file = Path(storage_file)
        self._ensure_default_user()
    
    def _ensure_default_user(self):
        """Ensure default admin user exists"""
        if not self.storage_file.exists():
            self.storage_file.parent.mkdir(parents=True, exist_ok=True)
            default_user = {
                "username": "admin",
                "password": self._hash_password("admin"),
                "full_name": "Administrator",
                "email": "admin@swisscom.com",
                "is_admin": True
            }
            self._save_users([default_user])
    
    def _hash_password(self, password: str) -> str:
        """Simple password hashing"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _load_users(self) -> List[dict]:
        """Load users from JSON file"""
        if not self.storage_file.exists():
            return []
        with open(self.storage_file, 'r') as f:
            data = json.load(f)
            return data.get("users", [])
    
    def _save_users(self, users: List[dict]):
        """Save users to JSON file"""
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_file, 'w') as f:
            json.dump({"users": users}, f, indent=2)
    
    def authenticate(self, username: str, password: str) -> Optional[UserInfo]:
        """Authenticate user and return user info"""
        users = self._load_users()
        password_hash = self._hash_password(password)
        
        for user in users:
            if user["username"] == username and user["password"] == password_hash:
                return UserInfo(
                    username=user["username"],
                    full_name=user["full_name"],
                    email=user["email"],
                    is_admin=user.get("is_admin", False)
                )
        return None
    
    def get_user(self, username: str) -> Optional[UserInfo]:
        """Get user info by username"""
        users = self._load_users()
        for user in users:
            if user["username"] == username:
                return UserInfo(
                    username=user["username"],
                    full_name=user["full_name"],
                    email=user["email"],
                    is_admin=user.get("is_admin", False)
                )
        return None
    
    def list_users(self) -> List[UserInfo]:
        """List all users (without passwords)"""
        users = self._load_users()
        return [
            UserInfo(
                username=user["username"],
                full_name=user["full_name"],
                email=user["email"],
                is_admin=user.get("is_admin", False)
            )
            for user in users
        ]
    
    def create_user(self, user_create: UserCreate) -> UserInfo:
        """Create a new user"""
        users = self._load_users()
        
        # Check if user already exists
        if any(u["username"] == user_create.username for u in users):
            raise ValueError("User already exists")
        
        # Add new user
        new_user = {
            "username": user_create.username,
            "password": self._hash_password(user_create.password),
            "full_name": user_create.full_name,
            "email": user_create.email,
            "is_admin": user_create.is_admin
        }
        users.append(new_user)
        self._save_users(users)
        
        return UserInfo(
            username=new_user["username"],
            full_name=new_user["full_name"],
            email=new_user["email"],
            is_admin=new_user["is_admin"]
        )
    
    def update_user(self, username: str, updates: dict) -> Optional[UserInfo]:
        """Update user information"""
        users = self._load_users()
        
        for user in users:
            if user["username"] == username:
                if "password" in updates:
                    user["password"] = self._hash_password(updates["password"])
                if "full_name" in updates:
                    user["full_name"] = updates["full_name"]
                if "email" in updates:
                    user["email"] = updates["email"]
                if "is_admin" in updates:
                    user["is_admin"] = updates["is_admin"]
                
                self._save_users(users)
                
                return UserInfo(
                    username=user["username"],
                    full_name=user["full_name"],
                    email=user["email"],
                    is_admin=user["is_admin"]
                )
        return None
    
    def delete_user(self, username: str) -> bool:
        """Delete a user"""
        users = self._load_users()
        original_length = len(users)
        users = [u for u in users if u["username"] != username]
        
        if len(users) < original_length:
            self._save_users(users)
            return True
        return False


user_storage = UserStorage()

