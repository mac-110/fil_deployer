# Configuration

This directory contains the customer configuration for FIL Deployer.

## customers.json

The `customers.json` file defines the customers, their GitLab repositories, and available stages.

### Example Structure

```json
{
  "customers": [
    {
      "id": "bcv",
      "name": "BCV",
      "repo_url": "https://code.swisscom.com/your-group/bcv-kpt-sif.git",
      "stages": ["dev", "tst", "prd"]
    }
  ]
}
```

### Fields

- **id**: Unique identifier for the customer (used in URLs)
- **name**: Display name for the customer
- **repo_url**: Full GitLab repository URL
- **stages**: Array of available stages for this customer

### Setup

1. Copy `customers.json.example` to `customers.json`
2. Update the configuration with your actual customer data
3. Ensure the `repo_url` values point to valid GitLab repositories

### Path Convention

The application expects the services.csv file to be located at:
```
{stage}/9620/sif/instance/stage/sif-services-pipeline/instance/config/services.csv
```

This path is consistent across all customer repositories.

