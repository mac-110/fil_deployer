import { useState, useEffect } from 'react';
import { Customer } from '../types';
import { configAPI } from '../services/api';
import './ConfigPanel.css';

export default function ConfigPanel() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');

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
      await configAPI.updateConfig(customers);
      setMessage('Configuration saved successfully!');
      setIsEditing(false);
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error saving configuration');
    } finally {
      setIsSaving(false);
    }
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
      <div className="config-header">
        <h2>Customer Configuration</h2>
        <button className="btn btn-add" onClick={handleAddCustomer}>
          + Add Customer
        </button>
      </div>

      {message && <div className="message">{message}</div>}

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

      <div className="config-footer">
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
      </div>
    </div>
  );
}

