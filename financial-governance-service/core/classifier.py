import json
import os
from typing import Dict, Any, Optional

class AgentClassifier:
    """
    Classifies AI Agents into Risk/Value tiers (RG, RS, OC) and calculates Innovation Friction.
    """
    
    def __init__(self, config_path: str = "config/taxonomy.json"):
        # Resolve config path relative to this file if needed, or assume running from root
        # For robustness, we'll try to find it relative to the script location
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(base_dir, config_path)
        self.config = self._load_config()
        self.friction_threshold = self.config["financial_constants"]["friction_guardrail_percent"]

    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def classify_agent(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classifies an agent based on its manifest and business metadata.
        """
        agent_type_code = manifest.get("agent_type", "OC") # Default to Operational Cost
        agent_type_def = self.config["agent_types"].get(agent_type_code)
        
        if not agent_type_def:
            raise ValueError(f"Unknown agent type: {agent_type_code}")

        # Validate mandatory fields
        if agent_type_def["opportunity_cost_required"]:
            if "opportunity_cost_per_hour" not in manifest or manifest["opportunity_cost_per_hour"] is None:
                 raise ValueError(f"Agent Type {agent_type_code} requires 'opportunity_cost_per_hour' to be defined.")

        classification = {
            "type_code": agent_type_code,
            "type_name": agent_type_def["name"],
            "risk_profile": agent_type_def["risk_profile"],
            "downtime_cost_per_hour": manifest.get("downtime_cost_per_hour", agent_type_def["default_downtime_cost_per_hour"]),
            "opportunity_cost_per_hour": manifest.get("opportunity_cost_per_hour", 0.0),
            "innovation_friction": self._calculate_friction(manifest)
        }
        
        return classification

    def _calculate_friction(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates Innovation Friction metrics.
        """
        estimated_loe_hours = manifest.get("governance_loe_hours", 0)
        total_dev_capacity_hours = manifest.get("total_dev_capacity_hours", 160) # Default 1 month FTE
        
        friction_percent = (estimated_loe_hours / total_dev_capacity_hours) * 100
        is_overrun = friction_percent > self.friction_threshold
        
        return {
            "loe_hours": estimated_loe_hours,
            "friction_percent": friction_percent,
            "is_overrun": is_overrun,
            "threshold": self.friction_threshold
        }

    def interactive_wizard(self) -> Dict[str, Any]:
        """
        CLI Wizard to intake agent details.
        """
        print("=== AI Agent Governance Intake Wizard ===")
        print("Please provide the following details:")
        
        name = input("Agent Name: ")
        
        print("\nAvailable Types:")
        for code, details in self.config["agent_types"].items():
            print(f"  [{code}] {details['name']}: {details['description']}")
            
        type_code = input("Agent Type Code [OC]: ") or "OC"
        
        downtime_cost = input(f"Downtime Cost per Hour ($) [Default]: ")
        downtime_cost = float(downtime_cost) if downtime_cost else None
        
        opp_cost = 0.0
        if self.config["agent_types"][type_code]["opportunity_cost_required"]:
            opp_cost_input = input("Opportunity Cost of Delay ($/hour) [REQUIRED]: ")
            opp_cost = float(opp_cost_input)
        else:
            opp_cost_input = input("Opportunity Cost of Delay ($/hour) [0.0]: ")
            opp_cost = float(opp_cost_input) if opp_cost_input else 0.0

        gov_loe = input("Estimated Governance LOE (hours) [0]: ")
        gov_loe = float(gov_loe) if gov_loe else 0.0
        
        manifest = {
            "name": name,
            "agent_type": type_code,
            "downtime_cost_per_hour": downtime_cost,
            "opportunity_cost_per_hour": opp_cost,
            "governance_loe_hours": gov_loe
        }
        
        return self.classify_agent(manifest)
