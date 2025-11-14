import { useState, useEffect } from 'react';
import Login from './components/Login';
import CustomerSelector from './components/CustomerSelector';
import ServiceEditor from './components/ServiceEditor';
import ConfigPanel from './components/ConfigPanel';
import UserManagement from './components/UserManagement';
import AppSettings from './components/AppSettings';
import { authAPI, customersAPI, servicesAPI } from './services/api';
import { Customer, Service, ServiceUpdate, UserInfo } from './types';
import './App.css';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<UserInfo | null>(null);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState('');
  const [selectedStage, setSelectedStage] = useState('');
  const [services, setServices] = useState<Service[]>([]);
  const [isLoadingServices, setIsLoadingServices] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [showConfig, setShowConfig] = useState(false);
  const [showUsers, setShowUsers] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const userData = await authAPI.getUser();
      setUser(userData);
      setIsAuthenticated(true);
      loadCustomers();
    } catch (error) {
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  const loadCustomers = async () => {
    try {
      const data = await customersAPI.getAll();
      setCustomers(data);
    } catch (error) {
      showMessage('Error loading customers', true);
    }
  };

  const loadServices = async (customerId: string, stage: string) => {
    setIsLoadingServices(true);
    setMessage('');
    try {
      const data = await servicesAPI.getServices(customerId, stage);
      setServices(data);
    } catch (error) {
      showMessage('Error loading services', true);
      setServices([]);
    } finally {
      setIsLoadingServices(false);
    }
  };

  const handleCustomerChange = (customerId: string) => {
    setSelectedCustomer(customerId);
    setSelectedStage('');
    setServices([]);
  };

  const handleStageChange = (stage: string) => {
    setSelectedStage(stage);
    if (selectedCustomer && stage) {
      loadServices(selectedCustomer, stage);
    }
  };

  const handleSaveServices = async (updatedServices: ServiceUpdate[], jiraTicket?: string, message?: string) => {
    setIsSaving(true);
    setMessage('');
    try {
      const response = await servicesAPI.saveServices(
        selectedCustomer,
        selectedStage,
        updatedServices,
        jiraTicket,
        message
      );
      showMessage(
        `${response.message}. Merge request created!`,
        false
      );
      if (response.merge_request_url) {
        setTimeout(() => {
          window.open(response.merge_request_url, '_blank');
        }, 1000);
      }
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Error saving services';
      showMessage(errorMsg, true);
    } finally {
      setIsSaving(false);
    }
  };

  const showMessage = (msg: string, isError: boolean) => {
    setMessage(msg);
    setTimeout(() => setMessage(''), isError ? 5000 : 10000);
  };

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      setIsAuthenticated(false);
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login onLoginSuccess={checkAuth} />;
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo-container">
              <img src="/swisscom-logo.gif" alt="Swisscom" />
              <h1>FIL Deployer</h1>
            </div>
          </div>
          <div className="header-actions">
            <span className="user-info">
              Welcome, {user?.full_name || user?.username}
              {user?.is_admin && <span className="admin-badge">Admin</span>}
            </span>
            {user?.is_admin && (
              <>
                <button 
                  className={`btn btn-secondary ${!showSettings && !showUsers && !showConfig ? 'active' : ''}`}
                  onClick={() => {
                    setShowSettings(false);
                    setShowConfig(false);
                    setShowUsers(false);
                  }}
                >
                  Services
                </button>
                <button 
                  className={`btn btn-secondary ${showSettings ? 'active' : ''}`}
                  onClick={() => {
                    setShowSettings(!showSettings);
                    setShowConfig(false);
                    setShowUsers(false);
                  }}
                >
                  Settings
                </button>
                <button 
                  className={`btn btn-secondary ${showUsers ? 'active' : ''}`}
                  onClick={() => {
                    setShowUsers(!showUsers);
                    setShowConfig(false);
                    setShowSettings(false);
                  }}
                >
                  Users
                </button>
                <button 
                  className={`btn btn-secondary ${showConfig ? 'active' : ''}`}
                  onClick={() => {
                    setShowConfig(!showConfig);
                    setShowUsers(false);
                    setShowSettings(false);
                  }}
                >
                  Customers
                </button>
              </>
            )}
            <button className="btn btn-secondary" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          {message && (
            <div className={`notification ${message.includes('Error') ? 'error' : 'success'}`}>
              {message}
            </div>
          )}

          {showSettings && user?.is_admin ? (
            <AppSettings />
          ) : showUsers && user?.is_admin ? (
            <UserManagement />
          ) : showConfig && user?.is_admin ? (
            <ConfigPanel />
          ) : (
            <>
              <CustomerSelector
                customers={customers}
                selectedCustomer={selectedCustomer}
                selectedStage={selectedStage}
                onCustomerChange={handleCustomerChange}
                onStageChange={handleStageChange}
              />

              {isLoadingServices && (
                <div className="loading-services">
                  <div className="spinner"></div>
                  <p>Loading services...</p>
                </div>
              )}

              {!isLoadingServices && services.length > 0 && (
                <ServiceEditor
                  services={services}
                  onSave={handleSaveServices}
                  isSaving={isSaving}
                />
              )}

              {!isLoadingServices && selectedStage && services.length === 0 && (
                <div className="no-services">
                  <p>No services found for this stage.</p>
                </div>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
}

