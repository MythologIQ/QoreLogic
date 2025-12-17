import unittest
from local_fortress.mcp_server.trust_engine import TrustEngine, TrustContext, TrustStage

class TestTrustEngine(unittest.TestCase):
    def setUp(self):
        self.engine = TrustEngine()
        
    def test_lambda_selection(self):
        self.assertEqual(self.engine.get_lambda(TrustContext.HIGH_RISK), 0.94)
        self.assertEqual(self.engine.get_lambda(TrustContext.LOW_RISK), 0.97)

    def test_ewma_update(self):
        # High Risk: 0.94
        current = 0.5
        new_score = self.engine.calculate_ewma_update(current, 1.0, TrustContext.HIGH_RISK)
        # 0.5 * 0.94 + 1.0 * 0.06 = 0.47 + 0.06 = 0.53
        self.assertAlmostEqual(new_score, 0.53)

    def test_transitive_trust(self):
        # Path [0.9, 0.9] -> 0.9 * 0.9 * 0.5 = 0.405
        res = self.engine.calculate_transitive_trust([0.9, 0.9])
        self.assertAlmostEqual(res, 0.405)

    def test_trust_stages(self):
        # Boundary checks
        self.assertEqual(self.engine.get_trust_stage(0.2), TrustStage.CBT)
        self.assertEqual(self.engine.get_trust_stage(0.5), TrustStage.CBT) 
        self.assertEqual(self.engine.get_trust_stage(0.51), TrustStage.KBT)
        self.assertEqual(self.engine.get_trust_stage(0.8), TrustStage.KBT)
        self.assertEqual(self.engine.get_trust_stage(0.81), TrustStage.IBT)

    def test_violation_demotion(self):
        # IBT -> Demote to KBT
        ibt_score = 0.95
        new_score = self.engine.calculate_violation_penalty(ibt_score)
        self.assertLessEqual(new_score, 0.8)
        self.assertEqual(self.engine.get_trust_stage(new_score), TrustStage.KBT)
        
        # KBT -> Demote to CBT
        kbt_score = 0.70
        new_score2 = self.engine.calculate_violation_penalty(kbt_score)
        self.assertLessEqual(new_score2, 0.5)
        self.assertEqual(self.engine.get_trust_stage(new_score2), TrustStage.CBT)
        
        # CBT -> Drop
        cbt_score = 0.40
        new_score3 = self.engine.calculate_violation_penalty(cbt_score)
        self.assertLess(new_score3, 0.40) # Should drop
        
        # Boundary case: already at ceiling (e.g. 0.8 exactly)
        kbt_ceiling = 0.8
        new_score4 = self.engine.calculate_violation_penalty(kbt_ceiling)
        self.assertLessEqual(new_score4, 0.5) # Force demote to CBT
        self.assertEqual(self.engine.get_trust_stage(new_score4), TrustStage.CBT)

if __name__ == '__main__':
    unittest.main()
