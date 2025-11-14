import requests
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ArtifactoryClient:
    """Client for interacting with Swisscom Artifactory"""
    
    BASE_URL = "https://bin.swisscom.com/artifactory/omega-fils-generic-local/gitlab"
    
    # Possible groups where FILs can be located
    GROUPS = ["fil", "bsa-camel3"]
    
    def __init__(self, token: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize Artifactory client
        
        Args:
            token: Optional authentication token for Artifactory
            base_url: Optional custom base URL (defaults to Swisscom Artifactory)
        """
        self.token = token
        self.base_url = base_url or self.BASE_URL
    
    def _get_headers(self) -> dict:
        """Get headers for requests, including authentication if token is set"""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def find_service_location(self, service_name: str, version: str) -> Optional[Tuple[str, str]]:
        """
        Find the correct group (fil or bsa-camel3) for a service
        
        Args:
            service_name: Name of the service
            version: Version of the service
            
        Returns:
            Tuple of (group, full_url) if found, None otherwise
        """
        for group in self.GROUPS:
            url = f"{self.base_url}/{group}/{service_name}/{service_name}-{version}.tgz"
            
            try:
                # Check if the artifact exists by making a HEAD request
                response = requests.head(url, headers=self._get_headers(), timeout=5)
                
                if response.status_code == 200:
                    logger.info(f"Found {service_name} {version} in group: {group}")
                    return (group, url)
                    
            except requests.RequestException as e:
                logger.warning(f"Error checking {url}: {str(e)}")
                continue
        
        logger.warning(f"Service {service_name} {version} not found in any group")
        return None
    
    def verify_url(self, url: str) -> bool:
        """
        Verify if a URL exists in Artifactory
        
        Args:
            url: Full URL to verify
            
        Returns:
            True if URL is accessible, False otherwise
        """
        try:
            response = requests.head(url, headers=self._get_headers(), timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    @staticmethod
    def get_group_from_url(url: str) -> Optional[str]:
        """
        Extract the group (fil or bsa-camel3) from a URL
        
        Args:
            url: Full Artifactory URL
            
        Returns:
            Group name if found in URL, None otherwise
        """
        for group in ArtifactoryClient.GROUPS:
            if f"/gitlab/{group}/" in url:
                return group
        return None

