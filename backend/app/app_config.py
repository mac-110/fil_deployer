import json
from pathlib import Path
from typing import Optional


class AppConfigManager:
    """Manage application configuration (tokens, etc.)"""
    
    def __init__(self, config_file: str = "config/app_config.json"):
        self.config_file = Path(config_file)
        self._ensure_default_config()
    
    def _ensure_default_config(self):
        """Ensure config file exists with defaults"""
        if not self.config_file.exists():
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            default_config = {
                "gitlab_url": "https://code.swisscom.com",
                "gitlab_group_token": "",
                "artifactory_url": "https://bin.swisscom.com",
                "artifactory_token": ""
            }
            self._save_config(default_config)
    
    def _load_config(self) -> dict:
        """Load configuration from JSON file"""
        if not self.config_file.exists():
            return {}
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def _save_config(self, config: dict):
        """Save configuration to JSON file"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_gitlab_token(self) -> Optional[str]:
        """Get GitLab group access token"""
        config = self._load_config()
        return config.get("gitlab_group_token")
    
    def get_gitlab_url(self) -> str:
        """Get GitLab URL"""
        config = self._load_config()
        return config.get("gitlab_url", "https://code.swisscom.com")
    
    def set_gitlab_token(self, token: str):
        """Set GitLab group access token"""
        config = self._load_config()
        config["gitlab_group_token"] = token
        self._save_config(config)
    
    def set_gitlab_url(self, url: str):
        """Set GitLab URL"""
        config = self._load_config()
        config["gitlab_url"] = url
        self._save_config(config)
    
    def get_artifactory_token(self) -> Optional[str]:
        """Get Artifactory access token"""
        config = self._load_config()
        return config.get("artifactory_token")
    
    def get_artifactory_url(self) -> str:
        """Get Artifactory URL"""
        config = self._load_config()
        return config.get("artifactory_url", "https://bin.swisscom.com")
    
    def set_artifactory_token(self, token: str):
        """Set Artifactory access token"""
        config = self._load_config()
        config["artifactory_token"] = token
        self._save_config(config)
    
    def set_artifactory_url(self, url: str):
        """Set Artifactory URL"""
        config = self._load_config()
        config["artifactory_url"] = url
        self._save_config(config)
    
    def get_all_config(self) -> dict:
        """Get all configuration (masked tokens)"""
        config = self._load_config()
        result = config.copy()
        # Mask tokens for security
        if result.get("gitlab_group_token"):
            token = result["gitlab_group_token"]
            if len(token) > 8:
                result["gitlab_group_token"] = token[:4] + "..." + token[-4:]
        if result.get("artifactory_token"):
            token = result["artifactory_token"]
            if len(token) > 8:
                result["artifactory_token"] = token[:4] + "..." + token[-4:]
        return result


app_config_manager = AppConfigManager()

