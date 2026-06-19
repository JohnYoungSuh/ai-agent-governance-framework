import argparse
import json
import sys
from core.classifier import AgentClassifier
from core.quantifier import FinancialQuantifier
from core.decision_maker import GovernanceOptimizer
from reports.pl_statement import PLGenerator

def main():
    parser = argparse.ArgumentParser(description="AI Governance Financial Engine")
    parser.add_argument("--wizard", action="store_true", help="Run interactive intake wizard")
    parser.add_argument("--manifest", type=str, help="Path to agent manifest JSON")
    parser.add_argument("--report-out", type=str, help="Path to save the P&L report")
    
    args = parser.parse_args()
    
    # Initialize Core Components
    classifier = AgentClassifier() # Assumes config/taxonomy.json relative to script or set up correctly
    quantifier = FinancialQuantifier()
    optimizer = GovernanceOptimizer(quantifier)
    reporter = PLGenerator()
    
    agent_classification = None
    
    if args.wizard:
        agent_classification = classifier.interactive_wizard()
    elif args.manifest:
        with open(args.manifest, 'r') as f:
            manifest = json.load(f)
        agent_classification = classifier.classify_agent(manifest)
    else:
        print("Error: Must provide --wizard or --manifest")
        parser.print_help()
        sys.exit(1)
        
    print(f"\n[INFO] Agent Classified as: {agent_classification['type_name']} ({agent_classification['type_code']})")
    print(f"[INFO] Innovation Friction: {agent_classification['innovation_friction']['friction_percent']:.1f}%")
    
    # Define Risk Scenarios (In a real app, these come from a Threat Intelligence Feed or Asset Profile)
    # Mocking standard risks for now
    risk_scenarios = [
        {"id": "hallucination", "aro_low": 2, "aro_likely": 10, "aro_high": 25, "sle": agent_classification["downtime_cost_per_hour"] * 4}, # 4 hour outage
        {"id": "data_leak", "aro_low": 0.1, "aro_likely": 0.5, "aro_high": 1.0, "sle": 1000000} # Regulatory fine
    ]
    
    # Define Posture Options (In a real app, these come from Policy Engine or NIST Mappings)
    # Mocking standard postures
    postures = [
        {
            "name": "Minimalist (Option C)",
            "cost_of_controls": 500.0,
            "delay_hours": 0,
            "effectiveness_map": {"hallucination": 0.1, "data_leak": 0.1},
            "maturity_level": 1.0
        },
        {
            "name": "Risk Transfer (Option B)",
            "cost_of_controls": 5000.0, # Insurance premium
            "delay_hours": 4, 
            "effectiveness_map": {"hallucination": 0.3, "data_leak": 0.9}, # Insurance pays for leak
            "maturity_level": 1.0
        },
        {
            "name": "Full Governance (Option A)",
            "cost_of_controls": 25000.0,
            "delay_hours": 48, # 2 days HITL
            "effectiveness_map": {"hallucination": 0.95, "data_leak": 0.95},
            "maturity_level": 1.0
        }
    ]
    
    # Run Optimization
    optimization_result = optimizer.optimize_posture(agent_classification, risk_scenarios, postures)
    
    # Calculate detailed NSV for the winner to feed into report
    # (The optimizer does this, but let's extract or recalculate if needed for detailed stats)
    # Assuming optimizer result contains sufficient data for the report
    
    # Generate Report
    report = reporter.generate_statement(agent_classification, optimization_result, {})
    
    print("\n" + "="*40)
    print(report)
    print("="*40)
    
    if args.report_out:
        with open(args.report_out, 'w') as f:
            f.write(report)
        print(f"\n[SUCCESS] Report saved to {args.report_out}")

if __name__ == "__main__":
    main()
