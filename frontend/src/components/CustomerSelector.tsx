import { Customer } from '../types';
import './CustomerSelector.css';

interface CustomerSelectorProps {
  customers: Customer[];
  selectedCustomer: string;
  selectedStage: string;
  onCustomerChange: (customerId: string) => void;
  onStageChange: (stage: string) => void;
}

export default function CustomerSelector({
  customers,
  selectedCustomer,
  selectedStage,
  onCustomerChange,
  onStageChange,
}: CustomerSelectorProps) {
  const customer = customers.find((c) => c.id === selectedCustomer);
  const stages = customer?.stages || [];

  // Sort customers alphabetically by name
  const sortedCustomers = [...customers].sort((a, b) =>
    a.name.localeCompare(b.name)
  );

  return (
    <div className="selector-container">
      <div className="selector-group">
        <label htmlFor="customer">Customer</label>
        <select
          id="customer"
          value={selectedCustomer}
          onChange={(e) => onCustomerChange(e.target.value)}
        >
          <option value="">Select a customer...</option>
          {sortedCustomers.map((customer) => (
            <option key={customer.id} value={customer.id}>
              {customer.name}
            </option>
          ))}
        </select>
      </div>

      {selectedCustomer && (
        <div className="selector-group">
          <label htmlFor="stage">Stage</label>
          <select
            id="stage"
            value={selectedStage}
            onChange={(e) => onStageChange(e.target.value)}
          >
            <option value="">Select a stage...</option>
            {stages.map((stage) => (
              <option key={stage} value={stage}>
                {stage.toUpperCase()}
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
}

