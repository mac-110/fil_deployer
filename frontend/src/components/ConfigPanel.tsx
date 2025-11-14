import { useState, useEffect } from 'react';
import { Customer } from '../types';
import { configAPI } from '../services/api';
import './ConfigPanel.css';

export default function ConfigPanel() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [editorMode, setEditorMode] = useState<'ui' | 'json'>('ui');
  const [jsonValue, setJsonValue] = useState('');

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const data = await configAPI.getConfig();
      setCustomers(data);
    } catch (error) {
      setMessage('Error loading configuration');
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setMessage('');
    try {
      // If in JSON mode, parse and validate JSON first
      if (editorMode === 'json') {
        try {
          const parsedData = JSON.parse(jsonValue);
          await configAPI.updateConfig(parsedData);
        } catch (parseError) {
          setMessage('Invalid JSON format');
          setIsSaving(false);
          return;
        }
      } else {
        await configAPI.updateConfig(customers);
      }
      setMessage('Configuration saved successfully!');
      setIsEditing(false);
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error saving configuration');
    } finally {
      setIsSaving(false);
    }
  };

  const handleModeSwitch = (mode: 'ui' | 'json') => {
    if (mode === 'json' && editorMode === 'ui') {
      // Switching from UI to JSON: serialize current customers
      setJsonValue(JSON.stringify(customers, null, 2));
    } else if (mode === 'ui' && editorMode === 'json') {
      // Switching from JSON to UI: parse JSON and update customers
      try {
        const parsedData = JSON.parse(jsonValue);
        setCustomers(parsedData);
      } catch (error) {
        setMessage('Invalid JSON - cannot switch to UI mode');
        return;
      }
    }
    setEditorMode(mode);
  };

  const handleAddCustomer = () => {
    setCustomers([
      ...customers,
      {
        id: '',
        name: '',
        repo_url: '',
        stages: [],
      },
    ]);
  };

  const handleRemoveCustomer = (index: number) => {
    setCustomers(customers.filter((_, i) => i !== index));
  };

  const handleCustomerChange = (
    index: number,
    field: keyof Customer,
    value: string | string[]
  ) => {
    const updated = [...customers];
    (updated[index] as any)[field] = value;
    setCustomers(updated);
  };

  if (!isEditing) {
    return (
      <div className="config-panel">
        <button className="btn btn-primary" onClick={() => setIsEditing(true)}>
          Edit Configuration
        </button>
      </div>
    );
  }

  return (
    <div className="config-panel">
      <div className="config-header-sticky">
        <div className="config-header">
          <h2>Customer Configuration</h2>
          <div className="config-header-actions">
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
              disabled={isSaving}
            >
              {isSaving ? 'Saving...' : 'Save Configuration'}
            </button>
            <div className="mode-toggle">
              <button
                className={`btn btn-mode ${editorMode === 'ui' ? 'active' : ''}`}
                onClick={() => handleModeSwitch('ui')}
              >
                UI Editor
              </button>
              <button
                className={`btn btn-mode ${editorMode === 'json' ? 'active' : ''}`}
                onClick={() => handleModeSwitch('json')}
              >
                JSON Editor
              </button>
            </div>
            {editorMode === 'ui' && (
              <button className="btn btn-add" onClick={handleAddCustomer}>
                + Add Customer
              </button>
            )}
          </div>
        </div>

        {message && <div className="message">{message}</div>}
      </div>

      <div className="config-content">
        {editorMode === 'ui' ? (
          <div className="config-list">
            {customers.map((customer, index) => (
              <div key={index} className="config-item">
                <div className="config-row">
                  <label>ID</label>
                  <input
                    type="text"
                    value={customer.id}
                    onChange={(e) => handleCustomerChange(index, 'id', e.target.value)}
                    placeholder="e.g., bcv"
                  />
                </div>
                <div className="config-row">
                  <label>Name</label>
                  <input
                    type="text"
                    value={customer.name}
                    onChange={(e) => handleCustomerChange(index, 'name', e.target.value)}
                    placeholder="e.g., BCV"
                  />
                </div>
                <div className="config-row">
                  <label>Repository URL</label>
                  <input
                    type="text"
                    value={customer.repo_url}
                    onChange={(e) => handleCustomerChange(index, 'repo_url', e.target.value)}
                    placeholder="https://code.swisscom.com/..."
                  />
                </div>
                <div className="config-row">
                  <label>Stages (comma-separated)</label>
                  <input
                    type="text"
                    value={customer.stages.join(', ')}
                    onChange={(e) =>
                      handleCustomerChange(
                        index,
                        'stages',
                        e.target.value.split(',').map((s) => s.trim())
                      )
                    }
                    placeholder="dev, tst, prd"
                  />
                </div>
                <button
                  className="btn btn-remove"
                  onClick={() => handleRemoveCustomer(index)}
                >
                  Remove Customer
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="json-editor">
            <textarea
              value={jsonValue}
              onChange={(e) => setJsonValue(e.target.value)}
              placeholder="Enter JSON configuration..."
              spellCheck={false}
            />
          </div>
        )}
      </div>
    </div>
  );
}

