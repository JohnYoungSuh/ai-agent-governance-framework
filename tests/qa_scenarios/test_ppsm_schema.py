import os
import json
import yaml
import jsonschema

def test_ppsm_registry_schema_validation():
    """Verify ppsm-registry.yml complies with policies/schemas/ppsm-entry.json"""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    schema_path = os.path.join(project_root, "policies/schemas/ppsm-entry.json")
    registry_path = os.path.join(project_root, "policies/ppsm/ppsm-registry.yml")
    
    with open(schema_path, "r") as f:
        schema = json.load(f)
        
    with open(registry_path, "r") as f:
        registry = yaml.safe_load(f)
        
    jsonschema.validate(instance=registry, schema=schema)
