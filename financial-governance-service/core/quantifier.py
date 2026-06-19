import math
from typing import Dict, Any, Tuple

class FinancialQuantifier:
    """
    Performs stochastic financial logic: ALE, NSV, and Confidence Intervals.
    """

    def __init__(self):
        pass

    def calculate_ale_stochastic(self, aro_low: float, aro_likely: float, aro_high: float, sle: float) -> Tuple[float, float]:
        """
        Calculates Annualized Loss Expectancy using Three-Point Estimation (PERT).
        Returns (ALE_Weighted, Standard_Deviation).
        """
        # PERT Weighted Average
        aro_weighted = (aro_low + 4 * aro_likely + aro_high) / 6.0
        
        # Standard Deviation of the ARO distribution (PERT approximation)
        aro_std_dev = (aro_high - aro_low) / 6.0
        
        ale_weighted = aro_weighted * sle
        ale_std_dev = aro_std_dev * sle
        
        return ale_weighted, ale_std_dev

    def calculate_ale_after(self, ale_before: float, effectiveness: float, maturity_multiplier: float) -> float:
        """
        Calculates ALE after governance controls are applied.
        Formula: ALE_After = ALE_Before * (1 - (Effectiveness * Maturity))
        """
        # Effectiveness: 0.0 to 1.0 (How good the control theoretically is)
        # Maturity: 0.0 to 1.0 (How well it's implemented)
        
        impact = effectiveness * maturity_multiplier
        ale_after = ale_before * (1.0 - impact)
        return max(0.0, ale_after)

    def calculate_nsv_stochastic(self, 
                                 ale_before_stats: Tuple[float, float], 
                                 ale_after: float, 
                                 cost_of_governance: float,
                                 opportunity_cost: float) -> Dict[str, float]:
        """
        Calculates Net Security Value with Confidence Intervals.
        NSV = (ALE_Before - ALE_After) - (Cost_of_Gov + Opportunity_Cost)
        """
        ale_before_mean, ale_before_std = ale_before_stats
        
        # Expected NSV
        nsv_mean = (ale_before_mean - ale_after) - (cost_of_governance + opportunity_cost)
        
        # For simplicity, assuming the uncertainty is dominated by ALE_Before.
        # 80% Confidence Interval (Z-score approx 1.28 for one-sided or +/- 1.28 for two-sided 80% coverage? 
        # Usually user means "We are 80% confident it's at least X" or +/- range.
        # Let's provide a range: Mean +/- 1.28 * StdDev
        
        z_score_80 = 1.28
        
        nsv_low = nsv_mean - (z_score_80 * ale_before_std)
        nsv_high = nsv_mean + (z_score_80 * ale_before_std)
        
        return {
            "nsv_mean": nsv_mean,
            "nsv_low_80_percent": nsv_low,
            "nsv_high_80_percent": nsv_high,
            "roi_ratio": nsv_mean / (cost_of_governance + opportunity_cost) if (cost_of_governance + opportunity_cost) > 0 else float('inf')
        }
