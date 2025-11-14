import json
from pathlib import Path
from typing import Optional
from .crypto_utils import crypto_manager


class AppConfigManager:
    """Manage application configuration with encrypted tokens"""

    # Field names that should be encrypted
    ENCRYPTED_FIELDS = {"gitlab_group_token", "artifactory_token"}

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

    def _encrypt_sensitive_fields(self, config: dict) -> dict:
        """
        Encrypt sensitive fields before saving.

        Args:
            config: Configuration dictionary

        Returns:
            Dictionary with encrypted sensitive fields
        """
        encrypted_config = config.copy()

        for field in self.ENCRYPTED_FIELDS:
            if field in encrypted_config and encrypted_config[field]:
                value = encrypted_config[field]
                # Only encrypt if not already encrypted
                if not crypto_manager.is_encrypted(value):
                    encrypted_config[field] = crypto_manager.encrypt(value)

        return encrypted_config

    def _decrypt_sensitive_fields(self, config: dict) -> dict:
        """
        Decrypt sensitive fields after loading.

        Args:
            config: Configuration dictionary with potentially encrypted fields

        Returns:
            Dictionary with decrypted sensitive fields
        """
        decrypted_config = config.copy()

        for field in self.ENCRYPTED_FIELDS:
            if field in decrypted_config and decrypted_config[field]:
                value = decrypted_config[field]
                # Only decrypt if encrypted
                if crypto_manager.is_encrypted(value):
                    try:
                        decrypted_config[field] = crypto_manager.decrypt(value)
                    except ValueError as e:
                        # If decryption fails, log and keep as empty
                        print(f"Warning: Failed to decrypt {field}: {e}")
                        decrypted_config[field] = ""

        return decrypted_config

    def _load_config(self) -> dict:
        """Load and decrypt configuration from JSON file"""
        if not self.config_file.exists():
            return {}

        with open(self.config_file, 'r') as f:
            encrypted_config = json.load(f)

        # Decrypt sensitive fields
        return self._decrypt_sensitive_fields(encrypted_config)

    def _save_config(self, config: dict):
        """Encrypt and save configuration to JSON file"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Encrypt sensitive fields before saving
        encrypted_config = self._encrypt_sensitive_fields(config)

        with open(self.config_file, 'w') as f:
            json.dump(encrypted_config, f, indent=2)

    def get_gitlab_token(self) -> Optional[str]:
        """Get decrypted GitLab group access token"""
        config = self._load_config()
        return config.get("gitlab_group_token")

    def get_gitlab_url(self) -> str:
        """Get GitLab URL"""
        config = self._load_config()
        return config.get("gitlab_url", "https://code.swisscom.com")

    def set_gitlab_token(self, token: str):
        """Set GitLab group access token (will be encrypted on save)"""
        config = self._load_config()
        config["gitlab_group_token"] = token
        self._save_config(config)

    def set_gitlab_url(self, url: str):
        """Set GitLab URL"""
        config = self._load_config()
        config["gitlab_url"] = url
        self._save_config(config)

    def get_artifactory_token(self) -> Optional[str]:
        """Get decrypted Artifactory access token"""
        config = self._load_config()
        return config.get("artifactory_token")

    def get_artifactory_url(self) -> str:
        """Get Artifactory URL"""
        config = self._load_config()
        return config.get("artifactory_url", "https://bin.swisscom.com")

    def set_artifactory_token(self, token: str):
        """Set Artifactory access token (will be encrypted on save)"""
        config = self._load_config()
        config["artifactory_token"] = token
        self._save_config(config)

    def set_artifactory_url(self, url: str):
        """Set Artifactory URL"""
        config = self._load_config()
        config["artifactory_url"] = url
        self._save_config(config)

    def get_all_config(self) -> dict:
        """Get all configuration (with masked tokens for display)"""
        config = self._load_config()
        result = config.copy()

        # Mask tokens for security (showing only first/last 4 chars)
        if result.get("gitlab_group_token"):
            token = result["gitlab_group_token"]
            if len(token) > 8:
                result["gitlab_group_token"] = token[:4] + "..." + token[-4:]
            else:
                result["gitlab_group_token"] = "•" * len(token)

        if result.get("artifactory_token"):
            token = result["artifactory_token"]
            if len(token) > 8:
                result["artifactory_token"] = token[:4] + "..." + token[-4:]
            else:
                result["artifactory_token"] = "•" * len(token)

        return result


app_config_manager = AppConfigManager()
