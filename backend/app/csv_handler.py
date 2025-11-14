import re
from typing import List, Dict, Optional
from .models import Service, ServiceUpdate
from .artifactory_client import ArtifactoryClient
import logging

logger = logging.getLogger(__name__)


class CSVHandler:
    """Handle parsing and normalization of services.csv files"""
    
    # Base URL pattern for Swisscom Artifactory
    BASE_URL = "https://bin.swisscom.com/artifactory/omega-fils-generic-local/gitlab"
    
    # Regex to parse service URLs (supports both fil and bsa-camel3 groups)
    # Also handles versions with git hashes like: 3.0.1_03a54be
    URL_PATTERN = re.compile(
        r'https://bin\.swisscom\.com/artifactory/omega-fils-generic-local/gitlab/'
        r'([^/]+)/([^/]+)/([^/]+)-([0-9.]+(?:_[a-zA-Z0-9]+)?)\.tgz'
    )
    
    # Cache for storing original URLs by service key (name:version)
    _url_cache: Dict[str, str] = {}
    
    @classmethod
    def parse_csv(cls, csv_content: str) -> List[Service]:
        """
        Parse services.csv content into Service objects
        
        Args:
            csv_content: Raw CSV file content (one URL per line)
            
        Returns:
            List of Service objects with parsed name and version
        """
        services = []
        lines = csv_content.strip().split('\n')
        
        # Clear the cache for this parsing session
        cls._url_cache.clear()
        
        for line in lines:
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            match = cls.URL_PATTERN.match(line)
            if match:
                group, service_name, service_name_repeat, version = match.groups()
                
                # Cache the original URL for this service
                cache_key = f"{service_name}:{version}"
                cls._url_cache[cache_key] = line
                
                # Use the service name from the path
                services.append(Service(
                    name=service_name,
                    version=version,
                    full_url=line
                ))
            else:
                # If URL doesn't match pattern, try to extract what we can
                logger.warning(f"URL doesn't match expected pattern: {line}")
                
                # Try to extract service name and version from non-standard URL
                # This is a best-effort attempt
                parts = line.split('/')
                if len(parts) >= 2:
                    filename = parts[-1]
                    # Try to extract name-version.tgz pattern
                    # More flexible pattern to handle various formats including git hashes
                    match_filename = re.match(r'(.+?)-([0-9]+(?:\.[0-9]+)*(?:_[a-zA-Z0-9]+)?)\.tgz', filename)
                    if match_filename:
                        service_name = match_filename.group(1)
                        version = match_filename.group(2)
                        
                        cache_key = f"{service_name}:{version}"
                        cls._url_cache[cache_key] = line
                        
                        logger.info(f"Successfully parsed non-standard URL: {service_name} {version}")
                        services.append(Service(
                            name=service_name,
                            version=version,
                            full_url=line
                        ))
                        continue
                
                # If we still can't parse it, store the full URL as cache key
                # This ensures we can at least preserve unknown URLs
                logger.error(f"Could not parse service URL, storing as-is: {line}")
                cache_key = f"unknown:{line}"
                cls._url_cache[cache_key] = line
                
                services.append(Service(
                    name="Unknown",
                    version="Unknown",
                    full_url=line
                ))
        
        return services
    
    @classmethod
    def normalize_service(cls, service: ServiceUpdate, artifactory_token: Optional[str] = None) -> str:
        """
        Convert a ServiceUpdate (name + version) back to full URL
        
        Uses cached URL if available, otherwise queries Artifactory to find
        the correct location (fil or bsa-camel3)
        
        Args:
            service: ServiceUpdate with name and version
            
        Returns:
            Full URL string for the service
        """
        # First, check if we have a cached URL for this service
        cache_key = f"{service.name}:{service.version}"
        if cache_key in cls._url_cache:
            logger.info(f"Using cached URL for {cache_key}")
            return cls._url_cache[cache_key]
        
        # If not in cache, query Artifactory to find the correct location
        logger.info(f"Querying Artifactory for {service.name} {service.version}")
        artifactory_client = ArtifactoryClient(token=artifactory_token)
        result = artifactory_client.find_service_location(service.name, service.version)
        
        if result:
            group, url = result
            # Cache the URL for future use
            cls._url_cache[cache_key] = url
            return url
        
        # Fallback: use heuristic based on service name
        # bsa-* services go to bsa-camel3 group
        # everything else goes to fil group
        logger.warning(
            f"Could not find {service.name} {service.version} in Artifactory, "
            "using heuristic"
        )
        
        if service.name.startswith('bsa-'):
            group = 'bsa-camel3'
        else:
            group = 'fil'
        
        # Construct the full URL
        url = (
            f"{cls.BASE_URL}/{group}/{service.name}/"
            f"{service.name}-{service.version}.tgz"
        )
        
        return url
    
    @classmethod
    def validate_services(cls, services: List[ServiceUpdate], artifactory_token: Optional[str] = None) -> List[str]:
        """
        Validate that all services exist in Artifactory
        
        Args:
            services: List of ServiceUpdate objects to validate
            artifactory_token: Optional Artifactory authentication token
            
        Returns:
            List of error messages for services that don't exist (empty if all valid)
        """
        errors = []
        artifactory_client = ArtifactoryClient(token=artifactory_token)
        
        for service in services:
            # Skip unknown services
            if not service.name or service.name.lower() == "unknown":
                continue
            if not service.version or service.version.lower() == "unknown":
                continue
            
            # Check if service exists in cache (from original CSV)
            cache_key = f"{service.name}:{service.version}"
            if cache_key in cls._url_cache:
                # Service was in original CSV, trust it
                logger.info(f"Service {cache_key} found in cache, skipping validation")
                continue
            
            # New or modified service - validate against Artifactory
            logger.info(f"Validating new/modified service: {service.name} {service.version}")
            result = artifactory_client.find_service_location(service.name, service.version)
            
            if not result:
                error_msg = f"Service '{service.name}' version '{service.version}' not found in Artifactory"
                logger.error(error_msg)
                errors.append(error_msg)
        
        return errors
    
    @classmethod
    def generate_csv(cls, services: List[ServiceUpdate], artifactory_token: Optional[str] = None) -> str:
        """
        Generate CSV content from list of services
        
        Args:
            services: List of ServiceUpdate objects
            artifactory_token: Optional Artifactory authentication token
            
        Returns:
            CSV content as string (one URL per line)
        """
        lines = []
        for service in services:
            # Skip services with unknown or empty names
            if not service.name or service.name.lower() == "unknown":
                logger.warning(f"Skipping service with unknown name: {service}")
                continue
            if not service.version or service.version.lower() == "unknown":
                logger.warning(f"Skipping service with unknown version: {service}")
                continue
                
            url = cls.normalize_service(service, artifactory_token)
            lines.append(url)
        
        # Add empty line at the end (as per original format)
        lines.append('')
        
        return '\n'.join(lines)

