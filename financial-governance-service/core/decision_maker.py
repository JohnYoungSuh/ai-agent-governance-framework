from typing import List, Dict, Any
from .quantifier import FinancialQuantifier

class GovernanceOptimizer:
    """
    The 'Patentable Core': An algorithm to optimize Governance Posture by minimizing Total Economic Cost.
    """
    
    def __init__(self, quantifier: FinancialQuantifier):
        self.quantifier = quantifier

    def optimize_posture(self, 
                         agent_classification: Dict[str, Any], 
                         risk_scenarios: List[Dict[str, Any]], 
                         posture_options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluates multiple governance postures and selects the best one.
        
        Total_Economic_Cost = Residual_Risk_ALE + Control_Cost + Opportunity_Cost
        """
        
        results = []
        
        for posture in posture_options:
            posture_name = posture["name"]
            control_cost = posture["cost_of_controls"]
            # Opportunity cost might scale with strictness (e.g., more strict = more delay)
            opp_cost_multiplier = posture.get("delay_multiplier", 1.0)
            opportunity_cost = agent_classification["opportunity_cost_per_hour"] * (posture.get("delay_hours", 0))
            
            maturity = posture.get("maturity_level", 0.5)
            
            total_residual_ale = 0.0
            total_ale_before = 0.0
            
            for scenario in risk_scenarios:
                # Calculate ALE Before
                sle = scenario["sle"]
                ale_before_mean, _ = self.quantifier.calculate_ale_stochastic(
                    scenario["aro_low"], scenario["aro_likely"], scenario["aro_high"], sle
                )
                total_ale_before += ale_before_mean
                
                # key: How effective is THIS posture against THIS scenario?
                effectiveness = posture.get("effectiveness_map", {}).get(scenario["id"], 0.0)
                
                # Calculate ALE After
                ale_after = self.quantifier.calculate_ale_after(ale_before_mean, effectiveness, maturity)
                total_residual_ale += ale_after
                
            total_economic_cost = total_residual_ale + control_cost + opportunity_cost
            
            results.append({
                "posture": posture_name,
                "residual_risk": total_residual_ale,
                "investment": control_cost + opportunity_cost,
                "total_economic_cost": total_economic_cost,
                "nsv": (total_ale_before - total_residual_ale) - (control_cost + opportunity_cost)
            })
            
        # Find minimum Total Economic Cost
        best_option = min(results, key=lambda x: x["total_economic_cost"])
        
        return {
            "recommended_posture": best_option["posture"],
            "analysis": results,
            "optimization_metric": "Total Economic Cost (Lower is Better)"
        }
