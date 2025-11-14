export interface Customer {
  id: string;
  name: string;
  repo_url: string;
  stages: string[];
}

export interface Service {
  name: string;
  version: string;
  full_url: string;
}

export interface ServiceUpdate {
  name: string;
  version: string;
}

export interface UserInfo {
  username: string;
  full_name: string;
  email: string;
  is_admin: boolean;
}

export interface UserCreate {
  username: string;
  password: string;
  full_name: string;
  email: string;
  is_admin: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface SaveServicesResponse {
  success: boolean;
  message: string;
  merge_request_url?: string;
}

export interface AppConfig {
  gitlab_url: string;
  gitlab_group_token: string;
  artifactory_url?: string;
  artifactory_token?: string;
}

