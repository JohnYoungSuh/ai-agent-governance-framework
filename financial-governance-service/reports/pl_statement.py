from typing import Dict, Any, List

class PLGenerator:
    """
    Generates P&L Statements for AI Governance.
    """
    
    def generate_statement(self, 
                           agent_classification: Dict[str, Any], 
                           optimization_result: Dict[str, Any], 
                           nsv_result: Dict[str, Any]) -> str:
        """
        Creates a markdown formatted P&L statement.
        """
        
        posture = optimization_result["recommended_posture"]
        
        # Extract financial data
        # Best option logic from the result
        best_option = next(item for item in optimization_result["analysis"] if item["posture"] == posture)
        
        residual_risk = best_option["residual_risk"]
        cost_of_controls = best_option["investment"] # Includes Opp Cost
        
        # NSV Calculation components from the Quantifier result (which might differ slightly if based on separate run, 
        # but let's assume consistent context or passed in)
        # We'll use the optimization result to derive the "Before" vs "After" context.
        
        # Contingent Liability = The potential loss that didn't happen (Value Preservation)
        # Ideally: Total ALE Before - Residual Risk
        # But let's use the explicit "NSV" which is Net Value.
        
        nsv = best_option["nsv"]
        
        report = f"""
# AI-Gov Financial P&L Statement

**Agent:** {agent_classification.get('name', 'Unknown')}
**Type:** {agent_classification['type_name']} ([{agent_classification['type_code']}])
**Selected Strategy:** {posture}

## 1. Executive Summary: AI Revenue at Risk
| Metric | Value | Notes |
| :--- | :--- | :--- |
| **Net Security Value (NSV)** | **${nsv:,.2f}** | Pure profit contribution from risk reduction |
| **TCO (Gov + Opportunity)** | ${cost_of_controls:,.2f} | Total Cost of Ownership for Governance |
| **Residual Risk** | ${residual_risk:,.2f} | Remaining annualized liability |

## 2. P&L Impact & Contingent Liability
This program effectively removed **${(nsv + cost_of_controls):,.2f}** of volatility from the balance sheet. 
This "Contingent Liability Reduction" represents money that *would have been lost* to incidents in an ungoverned state.

## 3. Innovation Friction Audit
- **Governance LOE:** {agent_classification['innovation_friction']['loe_hours']} hours
- **Friction Score:** {agent_classification['innovation_friction']['friction_percent']:.1f}% of capacity
"""

        if agent_classification['innovation_friction']['is_overrun']:
            report += "\n> [!WARNING]\n> **FRICTION OVERRUN**: Governance LOE exceeds the 10% guardrail limit. Immediate optimization required.\n"
        else:
            report += "\n> [!NOTE]\n> **FRICTION PASS**: Governance overhead is within acceptable limits.\n"
            
        return report
