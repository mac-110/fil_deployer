import { useState, useEffect } from 'react';
import { AppConfig } from '../types';
import { appConfigAPI } from '../services/api';
import './AppSettings.css';

export default function AppSettings() {
  const [config, setConfig] = useState<AppConfig>({
    gitlab_url: 'https://code.swisscom.com',
    gitlab_group_token: '',
    artifactory_url: 'https://bin.swisscom.com',
    artifactory_token: '',
  });
  const [isEditing, setIsEditing] = useState(false);
  const [message, setMessage] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const data = await appConfigAPI.getAppConfig();
      setConfig(data);
    } catch (error) {
      showMessage('Error loading configuration', true);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setMessage('');
    try {
      // Only send tokens if they were actually changed (not masked values)
      const configToSave = { ...config };
      
      // If GitLab token is masked (starts with dots or contains "..."), don't send it
      if (configToSave.gitlab_group_token && 
          (configToSave.gitlab_group_token.startsWith('•') || 
           configToSave.gitlab_group_token.includes('...'))) {
        configToSave.gitlab_group_token = '';
      }
      
      // If Artifactory token is masked (starts with dots or contains "..."), don't send it
      if (configToSave.artifactory_token && 
          (configToSave.artifactory_token.startsWith('•') || 
           configToSave.artifactory_token.includes('...'))) {
        configToSave.artifactory_token = '';
      }
      
      await appConfigAPI.updateAppConfig(configToSave);
      showMessage('Configuration saved successfully!', false);
      setIsEditing(false);
      loadConfig();
    } catch (error) {
      showMessage('Error saving configuration', true);
    } finally {
      setIsSaving(false);
    }
  };

  const showMessage = (msg: string, isError: boolean) => {
    setMessage(msg);
    setTimeout(() => setMessage(''), isError ? 5000 : 3000);
  };

  return (
    <div className="app-settings">
      <div className="section-header">
        <h2>Application Configuration</h2>
        {!isEditing && (
          <button className="btn btn-primary" onClick={() => setIsEditing(true)}>
            Edit
          </button>
        )}
      </div>

      {message && (
        <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}

      <div className="settings-form">
        <h3 className="subsection-title">GitLab Configuration</h3>
        
        <div className="form-group">
          <label>GitLab URL</label>
          <input
            type="text"
            value={config.gitlab_url}
            onChange={(e) => setConfig({ ...config, gitlab_url: e.target.value })}
            disabled={!isEditing}
            placeholder="https://code.swisscom.com"
          />
          <small>Your GitLab instance URL</small>
        </div>

        <div className="form-group">
          <label>Group Access Token</label>
          <input
            type={isEditing ? 'text' : 'password'}
            value={config.gitlab_group_token}
            onChange={(e) => setConfig({ ...config, gitlab_group_token: e.target.value })}
            disabled={!isEditing}
            placeholder={isEditing ? 'Enter new token' : '••••••••'}
          />
          <small>
            GitLab group access token with API and write_repository scopes.
            {!isEditing && config.gitlab_group_token && ' Token is masked for security.'}
          </small>
        </div>

        <h3 className="subsection-title">Artifactory Configuration</h3>
        
        <div className="form-group">
          <label>Artifactory URL</label>
          <input
            type="text"
            value={config.artifactory_url || 'https://bin.swisscom.com'}
            onChange={(e) => setConfig({ ...config, artifactory_url: e.target.value })}
            disabled={!isEditing}
            placeholder="https://bin.swisscom.com"
          />
          <small>Your Artifactory instance URL</small>
        </div>

        <div className="form-group">
          <label>Access Token (Optional)</label>
          <input
            type={isEditing ? 'text' : 'password'}
            value={config.artifactory_token || ''}
            onChange={(e) => setConfig({ ...config, artifactory_token: e.target.value })}
            disabled={!isEditing}
            placeholder={isEditing ? 'Enter token (optional)' : '••••••••'}
          />
          <small>
            Artifactory access token for authentication. Optional - only needed if Artifactory requires authentication.
            {!isEditing && config.artifactory_token && ' Token is masked for security.'}
          </small>
        </div>

        {isEditing && (
          <div className="form-actions">
            <button
              className="btn btn-secondary"
              onClick={() => {
                setIsEditing(false);
                loadConfig();
              }}
              disabled={isSaving}
            >
              Cancel
            </button>
            <button
              className="btn btn-primary"
              onClick={handleSave}
              disabled={isSaving || !config.gitlab_group_token}
            >
              {isSaving ? 'Saving...' : 'Save Configuration'}
            </button>
          </div>
        )}
      </div>

      <div className="info-box">
        <h3>How to create a GitLab Group Access Token:</h3>
        <ol>
          <li>Go to your GitLab group settings</li>
          <li>Navigate to "Access Tokens"</li>
          <li>Create a new token with these scopes:
            <ul>
              <li><code>api</code> - Full API access</li>
              <li><code>write_repository</code> - Write to repositories</li>
            </ul>
          </li>
          <li>Set role to <strong>Maintainer</strong></li>
          <li>Copy the token and paste it above</li>
        </ol>
      </div>
    </div>
  );
}

