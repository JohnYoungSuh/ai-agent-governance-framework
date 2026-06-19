import unittest
from core.quantifier import FinancialQuantifier
from core.classifier import AgentClassifier
from core.decision_maker import GovernanceOptimizer

class TestFinancialEngine(unittest.TestCase):
    
    def setUp(self):
        self.quantifier = FinancialQuantifier()
        # Mock classifier config for testing without file I/O dependency if possible, 
        # or just test logic that doesn't rely on config file loading if not needed.
        # Here we test quantifier main logic.
        
    def test_ale_stochastic(self):
        """Verify PERT Weighted Average Calculation"""
        # Low=10k, Likely=20k, High=50k. SLE=1.0 for simplicity.
        # Weighted = (10 + 4*20 + 50) / 6 = (140) / 6 = 23.33k
        low, likely, high = 10000, 20000, 50000
        ale, std_dev = self.quantifier.calculate_ale_stochastic(low, likely, high, 1.0)
        
        self.assertAlmostEqual(ale, 23333.33, places=2)
        # StdDev = (50k - 10k) / 6 = 6666.66
        self.assertAlmostEqual(std_dev, 6666.67, places=2)

    def test_nsv_confidence_interval(self):
        """Verify NSV math and confidence interval logic"""
        # ALE Before Stats: Mean=100k, Std=10k
        # ALE After: 20k
        # Cost: 10k, OppCost: 5k
        # NSV Mean = (100k - 20k) - (10k + 5k) = 80k - 15k = 65k
        
        ale_stats = (100000.0, 10000.0)
        nsv_result = self.quantifier.calculate_nsv_stochastic(ale_stats, 20000.0, 10000.0, 5000.0)
        
        self.assertEqual(nsv_result["nsv_mean"], 65000.0)
        # Low 80% CI = Mean - 1.28 * Std = 65k - 12.8k = 52.2k
        self.assertAlmostEqual(nsv_result["nsv_low_80_percent"], 52200.0, places=1)

    def test_sensitivity_analysis(self):
        """
        Verify that dropping effectiveness changes the decision.
        This simulates the 'Sensitivity Analysis' required by vCISO.
        """
        optimizer = GovernanceOptimizer(self.quantifier)
        
        # Mock Inputs
        agent = {"opportunity_cost_per_hour": 1000.0}
        
        scenarios = [{
            "id": "hallucination", 
            "aro_low": 2, "aro_likely": 5, "aro_high": 10, 
            "sle": 10000
        }] 
        # ALE Before approx: (2+20+10)/6 * 10k = 5.33 * 10k = 53.3k
        
        # Posture A: High Cost, High Effectiveness
        posture_a = {
            "name": "Heavy Governance",
            "cost_of_controls": 20000,
            "delay_hours": 10, # 10k opp cost
            "effectiveness_map": {"hallucination": 0.95},
            "maturity_level": 1.0
        }
        
        # Posture B: Low Cost, Low Effectiveness
        posture_b = {
            "name": "Light Governance",
            "cost_of_controls": 5000,
            "delay_hours": 0,
            "effectiveness_map": {"hallucination": 0.20},
            "maturity_level": 1.0
        }
        
        # Run 1: High Effectiveness
        result_1 = optimizer.optimize_posture(agent, scenarios, [posture_a, posture_b])
        # Posture A Residual: 53.3k * 0.05 = 2.6k. Cost = 20k + 10k = 30k. Total = 32.6k
        # Posture B Residual: 53.3k * 0.80 = 42.6k. Cost = 5k. Total = 47.6k
        # Winner should be A
        self.assertEqual(result_1["recommended_posture"], "Heavy Governance")
        
        # Run 2: Drop Effectiveness of A (e.g. Model Reliability drops)
        posture_a_degraded = posture_a.copy()
        posture_a_degraded["effectiveness_map"] = {"hallucination": 0.60}
        
        result_2 = optimizer.optimize_posture(agent, scenarios, [posture_a_degraded, posture_b])
        # Posture A Residual: 53.3k * 0.40 = 21.3k. Cost = 30k. Total = 51.3k
        # Posture B Total = 47.6k
        # Winner should now be B (or a different CP option) because A became too expensive for the value provided
        self.assertEqual(result_2["recommended_posture"], "Light Governance")

if __name__ == '__main__':
    unittest.main()
