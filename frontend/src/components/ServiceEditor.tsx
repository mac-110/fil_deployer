import { useState, useEffect, useMemo } from 'react';
import { Service, ServiceUpdate } from '../types';
import { servicesAPI } from '../services/api';
import './ServiceEditor.css';

interface ServiceEditorProps {
  services: Service[];
  onSave: (services: ServiceUpdate[], jiraTicket?: string, message?: string) => void;
  isSaving: boolean;
}

type SortField = 'name' | 'version';
type SortDirection = 'asc' | 'desc';

interface ValidationState {
  [key: number]: {
    isValidating: boolean;
    isValid: boolean;
    error?: string;
  };
}

export default function ServiceEditor({
  services,
  onSave,
  isSaving,
}: ServiceEditorProps) {
  const [editableServices, setEditableServices] = useState<ServiceUpdate[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<SortField>('name');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [jiraTicket, setJiraTicket] = useState('');
  const [message, setMessage] = useState('');
  const [validationState, setValidationState] = useState<ValidationState>({});

  useEffect(() => {
    const newServices = services.map((s) => ({ name: s.name, version: s.version }));
    setEditableServices(newServices);
    
    // Initialize all existing services as valid (from original CSV)
    const initialValidation: ValidationState = {};
    newServices.forEach((_, index) => {
      initialValidation[index] = {
        isValidating: false,
        isValid: true,
      };
    });
    setValidationState(initialValidation);
  }, [services]);

  // Extract major version from version string (e.g., "6.0.1" -> "6", "3.0.1_03a54be" -> "3")
  const getMajorVersion = (version: string): string | null => {
    const match = version.match(/^(\d+)\./);
    return match ? match[1] : null;
  };

  // Check for duplicate services with same major version
  const checkDuplicateMajorVersion = (services: ServiceUpdate[], currentIndex: number): { isDuplicate: boolean; error?: string } => {
    const current = services[currentIndex];
    if (!current.name.trim() || !current.version.trim()) {
      return { isDuplicate: false };
    }

    const currentMajor = getMajorVersion(current.version);
    if (!currentMajor) {
      return { isDuplicate: false };
    }

    // Check if any other service has the same name and major version
    for (let i = 0; i < services.length; i++) {
      if (i === currentIndex) continue;
      
      const other = services[i];
      if (!other.name.trim() || !other.version.trim()) continue;
      
      if (other.name.trim() === current.name.trim()) {
        const otherMajor = getMajorVersion(other.version);
        if (otherMajor === currentMajor) {
          return {
            isDuplicate: true,
            error: `Duplicate major version: ${current.name} v${currentMajor}.x.x already exists. Please change version of already existing ${current.name} v${currentMajor}.x.x`
          };
        }
      }
    }

    return { isDuplicate: false };
  };

  const handleServiceChange = async (index: number, field: 'name' | 'version', value: string) => {
    const updated = [...editableServices];
    updated[index][field] = value;
    setEditableServices(updated);
    
    // First check for duplicate major versions
    const duplicateCheck = checkDuplicateMajorVersion(updated, index);
    if (duplicateCheck.isDuplicate) {
      setValidationState(prev => ({
        ...prev,
        [index]: {
          isValidating: false,
          isValid: false,
          error: duplicateCheck.error
        }
      }));
      return;
    }

    // Trigger validation based on field state
    const service = updated[index];
    const hasName = service.name.trim() !== '';
    const hasVersion = service.version.trim() !== '';
    
    if (hasName && hasVersion) {
      // Both filled - validate against Artifactory
      setValidationState(prev => ({
        ...prev,
        [index]: { isValidating: true, isValid: false }
      }));
      
      try {
        const result = await servicesAPI.validateService(service);
        setValidationState(prev => ({
          ...prev,
          [index]: {
            isValidating: false,
            isValid: result.valid,
            error: result.error
          }
        }));
      } catch (error) {
        setValidationState(prev => ({
          ...prev,
          [index]: {
            isValidating: false,
            isValid: false,
            error: 'Validation failed'
          }
        }));
      }
    } else if (hasName || hasVersion) {
      // Only one field filled - invalid
      setValidationState(prev => ({
        ...prev,
        [index]: {
          isValidating: false,
          isValid: false,
          error: 'Both service name and version are required'
        }
      }));
    } else {
      // Both empty - valid (will be filtered out on save)
      setValidationState(prev => ({
        ...prev,
        [index]: { isValidating: false, isValid: true }
      }));
    }
  };

  const handleAddService = () => {
    const newIndex = editableServices.length;
    setEditableServices([...editableServices, { name: '', version: '' }]);
    setValidationState(prev => ({
      ...prev,
      [newIndex]: { isValidating: false, isValid: true }
    }));
  };

  const handleRemoveService = (index: number) => {
    const updated = editableServices.filter((_, i) => i !== index);
    setEditableServices(updated);
    
    // Remove validation state for this index and reindex remaining
    const newValidation: ValidationState = {};
    Object.keys(validationState).forEach(key => {
      const idx = parseInt(key);
      if (idx < index) {
        newValidation[idx] = validationState[idx];
      } else if (idx > index) {
        newValidation[idx - 1] = validationState[idx];
      }
    });
    setValidationState(newValidation);
  };

  const handleSave = () => {
    // Filter out empty services
    const validServices = editableServices.filter(
      (s) => s.name.trim() !== '' && s.version.trim() !== ''
    );
    onSave(validServices, jiraTicket || undefined, message || undefined);
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const filteredAndSortedServices = useMemo(() => {
    let filtered = editableServices.filter(service => 
      service.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      service.version.toLowerCase().includes(searchTerm.toLowerCase())
    );

    filtered.sort((a, b) => {
      const aValue = sortField === 'name' ? a.name : a.version;
      const bValue = sortField === 'name' ? b.name : b.version;
      
      const comparison = aValue.localeCompare(bValue);
      return sortDirection === 'asc' ? comparison : -comparison;
    });

    return filtered;
  }, [editableServices, searchTerm, sortField, sortDirection]);

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) return ' ↕';
    return sortDirection === 'asc' ? ' ↑' : ' ↓';
  };
  
  const hasInvalidServices = useMemo(() => {
    return Object.values(validationState).some(state => !state.isValid || state.isValidating);
  }, [validationState]);

  return (
    <div className="service-editor">
      <div className="editor-header">
        <h2>Services ({editableServices.length})</h2>
        <div className="editor-header-actions">
          <input
            type="text"
            className="search-input"
            placeholder="Search services..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button className="btn btn-add" onClick={handleAddService} disabled={isSaving}>
            + Add Service
          </button>
        </div>
      </div>

      <div className="services-table">
        <div className="table-header">
          <div 
            className="col-name sortable-header" 
            onClick={() => handleSort('name')}
          >
            Service Name{getSortIcon('name')}
          </div>
          <div 
            className="col-version sortable-header" 
            onClick={() => handleSort('version')}
          >
            Version{getSortIcon('version')}
          </div>
          <div className="col-actions">Actions</div>
        </div>

        <div className="table-body">
          {filteredAndSortedServices.length === 0 ? (
            <div className="no-results">
              {searchTerm ? 'No services found matching your search.' : 'No services available. Click "+ Add Service" to get started.'}
            </div>
          ) : (
                  filteredAndSortedServices.map((service) => {
                    const originalIndex = editableServices.findIndex(
                      s => s.name === service.name && s.version === service.version
                    );
                    const validation = validationState[originalIndex] || { isValidating: false, isValid: true };
                    const isInvalid = !validation.isValid && !validation.isValidating;
                    
                    return (
                      <div key={originalIndex} className={`table-row ${isInvalid ? 'invalid' : ''}`}>
                        <div className="col-name">
                          <input
                            type="text"
                            value={service.name}
                            onChange={(e) => handleServiceChange(originalIndex, 'name', e.target.value)}
                            placeholder="e.g., realEstateAdministration"
                            disabled={isSaving}
                            className={isInvalid ? 'invalid' : ''}
                          />
                        </div>
                        <div className="col-version">
                          <input
                            type="text"
                            value={service.version}
                            onChange={(e) => handleServiceChange(originalIndex, 'version', e.target.value)}
                            placeholder="e.g., 7.0.1"
                            disabled={isSaving}
                            className={isInvalid ? 'invalid' : ''}
                          />
                          {validation.isValidating && (
                            <span className="validation-spinner">⏳</span>
                          )}
                        </div>
                        <div className="col-actions">
                          <button
                            className="btn btn-remove"
                            onClick={() => handleRemoveService(originalIndex)}
                            disabled={isSaving}
                          >
                            Remove
                          </button>
                        </div>
                        {isInvalid && validation.error && (
                          <div className="validation-error">{validation.error}</div>
                        )}
                      </div>
                    );
                  })
          )}
        </div>
      </div>

      <div className="editor-footer">
        <div className="commit-info">
          <div className="commit-fields">
            <div className="form-group">
              <label htmlFor="jira-ticket">Jira Ticket (optional)</label>
              <input
                id="jira-ticket"
                type="text"
                value={jiraTicket}
                onChange={(e) => setJiraTicket(e.target.value)}
                placeholder="e.g., FOP-1234"
                disabled={isSaving}
              />
            </div>
            <div className="form-group">
              <label htmlFor="commit-message">Message (optional)</label>
              <input
                id="commit-message"
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Default: Updated services"
                disabled={isSaving}
              />
            </div>
          </div>
        </div>
        <button
          className="btn btn-save"
          onClick={handleSave}
          disabled={isSaving || editableServices.length === 0 || hasInvalidServices}
          title={hasInvalidServices ? 'Please fix validation errors before saving' : ''}
        >
          {isSaving ? 'Creating Merge Request...' : 'Save & Create MR'}
        </button>
      </div>
    </div>
  );
}

