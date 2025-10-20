// MongoDB Initialization Script
// AI Agent Governance Framework - Internal v2.1

// Switch to CMDB database
db = db.getSiblingDB('cmdb');

// Create collections
db.createCollection('configuration_items');
db.createCollection('baselines');
db.createCollection('change_requests');
db.createCollection('audit_trail');
db.createCollection('rmf_controls');
db.createCollection('drift_reports');
db.createCollection('itsi_services');
db.createCollection('itsi_kpis');
db.createCollection('itsi_entities');

// Create indexes for configuration_items
db.configuration_items.createIndex({ ci_id: 1 }, { unique: true });
db.configuration_items.createIndex({ ci_type: 1, environment: 1 });
db.configuration_items.createIndex({ 'relationships.target_ci_id': 1 });
db.configuration_items.createIndex({ configuration_hash: 1 });
db.configuration_items.createIndex({ tier: 1, environment: 1 });

// Create indexes for baselines
db.baselines.createIndex({ baseline_id: 1 }, { unique: true });
db.baselines.createIndex({ ci_id: 1, baseline_type: 1 });
db.baselines.createIndex({ status: 1, approved_at: -1 });
db.baselines.createIndex({ jira_cr_id: 1 });

// Create indexes for change_requests
db.change_requests.createIndex({ cr_id: 1 }, { unique: true });
db.change_requests.createIndex({ affected_cis: 1 });
db.change_requests.createIndex({ jira_cr_id: 1 });

// Create indexes for drift_reports
db.drift_reports.createIndex({ drift_id: 1 }, { unique: true });
db.drift_reports.createIndex({ ci_id: 1, detected_at: -1 });
db.drift_reports.createIndex({ severity: 1, remediation_required: 1 });

// Create indexes for ITSI collections
db.itsi_services.createIndex({ service_id: 1 }, { unique: true });
db.itsi_services.createIndex({ service_name: 1 });
db.itsi_kpis.createIndex({ kpi_id: 1 }, { unique: true });
db.itsi_kpis.createIndex({ service_id: 1 });
db.itsi_entities.createIndex({ entity_id: 1 }, { unique: true });
db.itsi_entities.createIndex({ entity_type: 1 });

print('CMDB database initialized successfully');
print('Collections created: ' + db.getCollectionNames().length);
