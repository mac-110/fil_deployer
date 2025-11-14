import axios from 'axios';
import { Customer, Service, ServiceUpdate, UserInfo, SaveServicesResponse, LoginRequest, UserCreate, AppConfig } from '../types';

const api = axios.create({
  baseURL: '',
  withCredentials: true,
});

export const authAPI = {
  login: async (credentials: LoginRequest): Promise<UserInfo> => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },
  
  logout: async () => {
    await api.post('/auth/logout');
  },
  
  getUser: async (): Promise<UserInfo> => {
    const response = await api.get('/auth/user');
    return response.data;
  },
};

export const customersAPI = {
  getAll: async (): Promise<Customer[]> => {
    const response = await api.get('/api/customers');
    return response.data;
  },
  
  getStages: async (customerId: string): Promise<string[]> => {
    const response = await api.get(`/api/customers/${customerId}/stages`);
    return response.data;
  },
};

export const servicesAPI = {
  getServices: async (customerId: string, stage: string): Promise<Service[]> => {
    const response = await api.get(`/api/services/${customerId}/${stage}`);
    return response.data;
  },
  
  validateService: async (service: ServiceUpdate): Promise<{ valid: boolean; error?: string }> => {
    const response = await api.post(`/api/services/validate`, service);
    return response.data;
  },
  
  saveServices: async (
    customerId: string,
    stage: string,
    services: ServiceUpdate[],
    jiraTicket?: string,
    message?: string
  ): Promise<SaveServicesResponse> => {
    const response = await api.post(`/api/services/${customerId}/${stage}`, {
      services,
      jira_ticket: jiraTicket,
      message,
    });
    return response.data;
  },
};

export const configAPI = {
  getConfig: async (): Promise<Customer[]> => {
    const response = await api.get('/api/config');
    return response.data;
  },
  
  updateConfig: async (customers: Customer[]): Promise<void> => {
    await api.put('/api/config', customers);
  },
};

export const userAPI = {
  listUsers: async (): Promise<UserInfo[]> => {
    const response = await api.get('/api/users');
    return response.data;
  },
  
  createUser: async (user: UserCreate): Promise<UserInfo> => {
    const response = await api.post('/api/users', user);
    return response.data;
  },
  
  updateUser: async (username: string, updates: any): Promise<UserInfo> => {
    const response = await api.put(`/api/users/${username}`, updates);
    return response.data;
  },
  
  deleteUser: async (username: string): Promise<void> => {
    await api.delete(`/api/users/${username}`);
  },
};

export const appConfigAPI = {
  getAppConfig: async (): Promise<AppConfig> => {
    const response = await api.get('/api/app-config');
    return response.data;
  },
  
  updateAppConfig: async (config: AppConfig): Promise<void> => {
    await api.put('/api/app-config', config);
  },
};

