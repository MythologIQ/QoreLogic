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

    def test_micro_penalties(self):
        from local_fortress.mcp_server.trust_engine import MicroPenaltyType
        
        start_score = 0.5
        # 1. Normal penalty
        new_score, applied = self.engine.calculate_micro_penalty(start_score, MicroPenaltyType.SCHEMA_VIOLATION, 0.0)
        self.assertAlmostEqual(applied, 0.005)
        self.assertAlmostEqual(new_score, 0.495)
        
        # 2. Capped penalty
        # Daily sum already 0.019. Cap is 0.020. Remaining 0.001.
        # Penalty is 0.005. Should apply only 0.001.
        new_score2, applied2 = self.engine.calculate_micro_penalty(start_score, MicroPenaltyType.SCHEMA_VIOLATION, 0.019)
        self.assertAlmostEqual(applied2, 0.001)
        self.assertAlmostEqual(new_score2, start_score - 0.001)

    def test_probation(self):
        import time
        now = time.time()
        
        # New agent (0 verifies, 0 age) -> Probation True
        self.assertTrue(self.engine.is_in_probation(now, 0))
        
        # 5 verifications -> Probation False
        self.assertFalse(self.engine.is_in_probation(now, 5))
        
        # 31 days old -> Probation False
        old_time = now - (31 * 24 * 3600)
        self.assertFalse(self.engine.is_in_probation(old_time, 0))

if __name__ == '__main__':
    unittest.main()
