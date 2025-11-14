import json
import os
from typing import List, Optional
from pathlib import Path
from .models import Customer


class Config:
    def __init__(self):
        self.gitlab_url = os.getenv("GITLAB_URL", "https://code.swisscom.com")
        self.gitlab_client_id = os.getenv("GITLAB_CLIENT_ID")
        self.gitlab_client_secret = os.getenv("GITLAB_CLIENT_SECRET")
        self.gitlab_group_token = os.getenv("GITLAB_GROUP_TOKEN")
        self.session_secret = os.getenv("SESSION_SECRET", "change-me-in-production")
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        self.config_file = os.getenv("CONFIG_FILE", "config/customers.json")
        
        # Git clone cache directory
        self.git_cache_dir = os.getenv("GIT_CACHE_DIR", "/tmp/fil-deployer-repos")
        Path(self.git_cache_dir).mkdir(parents=True, exist_ok=True)
        
    def load_customers(self) -> List[Customer]:
        """Load customer configurations from JSON file"""
        config_path = Path(self.config_file)
        if not config_path.exists():
            return []
        
        with open(config_path, 'r') as f:
            data = json.load(f)
            return [Customer(**customer) for customer in data.get("customers", [])]
    
    def save_customers(self, customers: List[Customer]):
        """Save customer configurations to JSON file"""
        config_path = Path(self.config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            data = {"customers": [customer.dict() for customer in customers]}
            json.dump(data, f, indent=2)
    
    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get a specific customer by ID"""
        customers = self.load_customers()
        for customer in customers:
            if customer.id == customer_id:
                return customer
        return None


config = Config()

