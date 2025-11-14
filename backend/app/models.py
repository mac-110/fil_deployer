from pydantic import BaseModel
from typing import List, Optional


class Customer(BaseModel):
    id: str
    name: str
    repo_url: str
    stages: List[str]
    csv_path_template: str = "{stage}/9620/sif/instance/stage/sif-services-pipeline/instance/config/services.csv"


class Service(BaseModel):
    name: str
    version: str
    full_url: str


class ServiceUpdate(BaseModel):
    name: str
    version: str


class SaveServicesRequest(BaseModel):
    services: List[ServiceUpdate]
    jira_ticket: Optional[str] = None
    message: Optional[str] = None


class SaveServicesResponse(BaseModel):
    success: bool
    message: str
    merge_request_url: Optional[str] = None


class User(BaseModel):
    username: str
    password: str
    full_name: str
    email: str
    is_admin: bool = False


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    email: str
    is_admin: bool = False


class UserInfo(BaseModel):
    username: str
    full_name: str
    email: str
    is_admin: bool


class LoginRequest(BaseModel):
    username: str
    password: str


class AppConfig(BaseModel):
    gitlab_group_token: str
    gitlab_url: str = "https://code.swisscom.com"
    artifactory_token: Optional[str] = None
    artifactory_url: str = "https://bin.swisscom.com"

