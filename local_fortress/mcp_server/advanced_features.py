"""
Q-DNA P2 Advanced Features

Implements:
1. Deferral Windows - Time-boxed disclosure (4h/24h/72h)
2. Operational Mode Enforcement - LEAN/SURGE/SAFE behavior
3. Calibration Error Tracking - Brier score for overconfidence detection
4. Reputation Auto-Recovery - 1% per clean audit
"""

import sqlite3
import time
import json
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).parent.parent / "ledger" / "qdna_soa_ledger.db"


# =============================================================================
# 1. Deferral Windows
# =============================================================================

class DeferralCategory(Enum):
    """Deferral categories with max windows per spec Section 8.2"""
    SAFETY_CRITICAL = 4 * 3600      # 4 hours
    MEDICAL = 24 * 3600             # 24 hours
    LEGAL = 24 * 3600               # 24 hours
    FINANCIAL = 24 * 3600           # 24 hours
    REPUTATIONAL = 72 * 3600        # 72 hours
    LOW_RISK = 0                    # No deferral


@dataclass
class DeferralRequest:
    """A deferred disclosure request."""
    deferral_id: int
    artifact_hash: str
    category: str
    reason: str
    start_time: float
    max_end_time: float
    actual_disclosed_at: Optional[float]
    status: str  # DEFERRED, DISCLOSED, EXPIRED, FORCED


class DeferralManager:
    """Manages time-boxed disclosure deferrals."""
    
    def __init__(self):
        self._ensure_schema()
    
    @contextmanager
    def get_db(self):
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _ensure_schema(self):
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS disclosure_deferral (
                    deferral_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    artifact_hash TEXT NOT NULL,
                    category TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    max_end_time REAL NOT NULL,
                    actual_disclosed_at REAL,
                    status TEXT DEFAULT 'DEFERRED' CHECK(status IN ('DEFERRED', 'DISCLOSED', 'EXPIRED', 'FORCED'))
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_deferral_status ON disclosure_deferral(status)
            """)
            conn.commit()
    
    def request_deferral(
        self, 
        artifact_hash: str, 
        category: DeferralCategory,
        reason: str
    ) -> DeferralRequest:
        """
        Request a deferral for sensitive disclosure.
        
        Returns:
            DeferralRequest with maximum allowed window
        """
        now = time.time()
        max_duration = category.value
        
        if max_duration == 0:
            # No deferral allowed
            return DeferralRequest(
                deferral_id=0,
                artifact_hash=artifact_hash,
                category=category.name,
                reason="LOW_RISK: No deferral allowed",
                start_time=now,
                max_end_time=now,
                actual_disclosed_at=now,
                status="DISCLOSED"
            )
        
        max_end = now + max_duration
        
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO disclosure_deferral 
                (artifact_hash, category, reason, start_time, max_end_time, status)
                VALUES (?, ?, ?, ?, ?, 'DEFERRED')
            """, (artifact_hash, category.name, reason, now, max_end))
            conn.commit()
            
            return DeferralRequest(
                deferral_id=cursor.lastrowid,
                artifact_hash=artifact_hash,
                category=category.name,
                reason=reason,
                start_time=now,
                max_end_time=max_end,
                actual_disclosed_at=None,
                status="DEFERRED"
            )
    
    def complete_disclosure(self, deferral_id: int) -> Dict:
        """Mark a deferral as disclosed."""
        now = time.time()
        
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE disclosure_deferral 
                SET status = 'DISCLOSED', actual_disclosed_at = ?
                WHERE deferral_id = ? AND status = 'DEFERRED'
            """, (now, deferral_id))
            conn.commit()
            
            return {"deferral_id": deferral_id, "disclosed_at": now}
    
    def check_expired_deferrals(self) -> List[DeferralRequest]:
        """Find and expire overdue deferrals."""
        now = time.time()
        expired = []
        
        with self.get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM disclosure_deferral 
                WHERE status = 'DEFERRED' AND max_end_time < ?
            """, (now,))
            
            for row in cursor.fetchall():
                expired.append(DeferralRequest(
                    deferral_id=row["deferral_id"],
                    artifact_hash=row["artifact_hash"],
                    category=row["category"],
                    reason=row["reason"],
                    start_time=row["start_time"],
                    max_end_time=row["max_end_time"],
                    actual_disclosed_at=None,
                    status="EXPIRED"
                ))
            
            # Mark as expired
            cursor.execute("""
                UPDATE disclosure_deferral 
                SET status = 'EXPIRED'
                WHERE status = 'DEFERRED' AND max_end_time < ?
            """, (now,))
            conn.commit()
        
        return expired
    
    def get_active_deferrals(self) -> List[Dict]:
        """Get all currently active deferrals."""
        now = time.time()
        
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM disclosure_deferral 
                WHERE status = 'DEFERRED'
                ORDER BY max_end_time ASC
            """)
            
            results = []
            for row in cursor.fetchall():
                remaining = max(0, row["max_end_time"] - now)
                results.append({
                    "deferral_id": row["deferral_id"],
                    "category": row["category"],
                    "remaining_hours": remaining / 3600,
                    "expires_at": row["max_end_time"]
                })
            
            return results


# =============================================================================
# 2. Operational Mode Enforcement
# =============================================================================

class OperationalMode(Enum):
    NORMAL = "NORMAL"   # 100% verification
    LEAN = "LEAN"       # L1 sampling (10%)
    SURGE = "SURGE"     # L1 deferred
    SAFE = "SAFE"       # Human-only mode


class ModeEnforcer:
    """Enforces operational mode rules per spec Section 12."""
    
    L1_SAMPLE_RATE = 0.10  # 10% sampling in LEAN mode
    
    def __init__(self):
        pass
    
    @contextmanager
    def get_db(self):
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def get_current_mode(self) -> str:
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT current_mode FROM system_state WHERE state_id = 1")
            row = cursor.fetchone()
            return row[0] if row else "NORMAL"
    
    def should_verify(self, risk_grade: str) -> Tuple[bool, str]:
        """
        Determine if verification should proceed based on mode and grade.
        
        Returns:
            (should_verify: bool, reason: str)
        """
        mode = self.get_current_mode()
        
        if mode == "NORMAL":
            return True, "NORMAL mode: Full verification"
        
        elif mode == "LEAN":
            if risk_grade == "L1":
                # 10% sampling for L1
                if random.random() < self.L1_SAMPLE_RATE:
                    return True, "LEAN mode: L1 sampled for verification"
                else:
                    return False, "LEAN mode: L1 skipped (sampling)"
            else:
                return True, "LEAN mode: L2/L3 full verification"
        
        elif mode == "SURGE":
            if risk_grade == "L1":
                return False, "SURGE mode: L1 deferred"
            else:
                return True, "SURGE mode: L2/L3 prioritized"
        
        elif mode == "SAFE":
            if risk_grade == "L3":
                return True, "SAFE mode: L3 requires Overseer"
            else:
                return False, "SAFE mode: Non-L3 suspended"
        
        return True, "Unknown mode: Defaulting to verify"
    
    def get_mode_stats(self) -> Dict:
        """Get statistics about mode behavior."""
        mode = self.get_current_mode()
        
        return {
            "current_mode": mode,
            "l1_behavior": {
                "NORMAL": "100% verified",
                "LEAN": "10% sampled",
                "SURGE": "Deferred",
                "SAFE": "Suspended"
            }.get(mode, "Unknown"),
            "l2_behavior": {
                "NORMAL": "100% verified",
                "LEAN": "100% verified",
                "SURGE": "100% verified",
                "SAFE": "Suspended"
            }.get(mode, "Unknown"),
            "l3_behavior": "100% verified (never compromised)"
        }


# =============================================================================
# 3. Calibration Error Tracking (Brier Score)
# =============================================================================

@dataclass
class CalibrationRecord:
    """A calibration measurement for an agent."""
    agent_did: str
    prediction_confidence: float  # 0-1
    actual_outcome: bool          # True if prediction was correct
    brier_contribution: float     # (confidence - outcome)^2
    timestamp: float


class CalibrationTracker:
    """
    Tracks agent calibration using Brier Score.
    
    Brier Score = mean((confidence - outcome)^2)
    - 0.0 = Perfect calibration
    - 0.25 = Random guessing
    - 1.0 = Always wrong with high confidence
    
    Per spec: Error > 0.2 triggers Honest Error Track
    """
    
    HONEST_ERROR_THRESHOLD = 0.2
    WINDOW_SIZE = 100  # Rolling window for Brier calculation
    
    def __init__(self):
        self._ensure_schema()
    
    @contextmanager
    def get_db(self):
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _ensure_schema(self):
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calibration_log (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_did TEXT NOT NULL,
                    prediction_confidence REAL NOT NULL,
                    actual_outcome INTEGER NOT NULL,
                    brier_contribution REAL NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_calibration_agent 
                ON calibration_log(agent_did)
            """)
            conn.commit()
    
    def record_prediction(
        self, 
        agent_did: str, 
        confidence: float, 
        correct: bool
    ) -> CalibrationRecord:
        """
        Record a prediction outcome for calibration tracking.
        
        Args:
            agent_did: The agent's DID
            confidence: How confident the agent was (0-1)
            correct: Whether the prediction was correct
        """
        outcome = 1.0 if correct else 0.0
        brier = (confidence - outcome) ** 2
        now = time.time()
        
        record = CalibrationRecord(
            agent_did=agent_did,
            prediction_confidence=confidence,
            actual_outcome=correct,
            brier_contribution=brier,
            timestamp=now
        )
        
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO calibration_log 
                (agent_did, prediction_confidence, actual_outcome, brier_contribution, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (agent_did, confidence, int(correct), brier, now))
            conn.commit()
        
        return record
    
    def get_brier_score(self, agent_did: str) -> Optional[float]:
        """Calculate rolling Brier score for an agent."""
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT AVG(brier_contribution) as brier
                FROM (
                    SELECT brier_contribution 
                    FROM calibration_log 
                    WHERE agent_did = ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                )
            """, (agent_did, self.WINDOW_SIZE))
            
            row = cursor.fetchone()
            return row[0] if row and row[0] is not None else None
    
    def check_honest_error_trigger(self, agent_did: str) -> Tuple[bool, Optional[float]]:
        """
        Check if agent's Brier score triggers Honest Error Track.
        
        Returns:
            (triggered: bool, brier_score: float or None)
        """
        brier = self.get_brier_score(agent_did)
        
        if brier is None:
            return False, None
        
        return brier > self.HONEST_ERROR_THRESHOLD, brier
    
    def get_calibration_report(self, agent_did: str) -> Dict:
        """Get detailed calibration report for an agent."""
        with self.get_db() as conn:
            cursor = conn.cursor()
            
            # Get Brier score
            brier = self.get_brier_score(agent_did)
            
            # Get prediction count
            cursor.execute("""
                SELECT COUNT(*) as count FROM calibration_log WHERE agent_did = ?
            """, (agent_did,))
            count = cursor.fetchone()[0]
            
            # Get accuracy
            cursor.execute("""
                SELECT AVG(actual_outcome) as accuracy FROM calibration_log WHERE agent_did = ?
            """, (agent_did,))
            accuracy = cursor.fetchone()[0]
            
            # Get average confidence
            cursor.execute("""
                SELECT AVG(prediction_confidence) as avg_conf FROM calibration_log WHERE agent_did = ?
            """, (agent_did,))
            avg_conf = cursor.fetchone()[0]
        
        triggered, _ = self.check_honest_error_trigger(agent_did)
        
        return {
            "agent_did": agent_did,
            "brier_score": round(brier, 4) if brier else None,
            "prediction_count": count,
            "accuracy": round(accuracy, 4) if accuracy else None,
            "average_confidence": round(avg_conf, 4) if avg_conf else None,
            "calibration_status": "OVERCONFIDENT" if triggered else "OK",
            "honest_error_triggered": triggered
        }


# =============================================================================
# 4. Reputation Auto-Recovery
# =============================================================================

class ReputationRecovery:
    """
    Manages automatic reputation recovery for agents.
    
    Per spec: Clean audits restore 1% weight per successful verification.
    Maximum weight: 2.0
    """
    
    RECOVERY_RATE = 0.01  # 1% per clean audit
    MAX_WEIGHT = 2.0
    MIN_WEIGHT = 0.0
    
    def __init__(self):
        pass
    
    @contextmanager
    def get_db(self):
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def record_clean_audit(self, agent_did: str) -> Dict:
        """
        Record a clean audit and potentially increase reputation.
        
        Returns:
            Dict with old weight, new weight, and recovery applied
        """
        with self.get_db() as conn:
            cursor = conn.cursor()
            
            # Get current weight
            cursor.execute(
                "SELECT influence_weight FROM agent_registry WHERE did = ?", 
                (agent_did,)
            )
            row = cursor.fetchone()
            
            if not row:
                return {"error": f"Agent {agent_did} not found"}
            
            old_weight = row[0]
            
            # Only recover if below max
            if old_weight >= self.MAX_WEIGHT:
                return {
                    "agent_did": agent_did,
                    "old_weight": old_weight,
                    "new_weight": old_weight,
                    "recovery_applied": False,
                    "reason": "Already at maximum weight"
                }
            
            new_weight = min(self.MAX_WEIGHT, old_weight + self.RECOVERY_RATE)
            
            # Update weight
            cursor.execute("""
                UPDATE agent_registry 
                SET influence_weight = ?, updated_at = datetime('now')
                WHERE did = ?
            """, (new_weight, agent_did))
            
            # Log the recovery
            cursor.execute("""
                INSERT INTO reputation_log 
                (agent_did, previous_weight, new_weight, adjustment, reason)
                VALUES (?, ?, ?, ?, ?)
            """, (agent_did, old_weight, new_weight, self.RECOVERY_RATE, "Clean audit auto-recovery"))
            
            conn.commit()
            
            return {
                "agent_did": agent_did,
                "old_weight": round(old_weight, 4),
                "new_weight": round(new_weight, 4),
                "recovery_applied": True,
                "delta": round(new_weight - old_weight, 4)
            }
    
    def get_recovery_history(self, agent_did: str, limit: int = 10) -> List[Dict]:
        """Get recent recovery history for an agent."""
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM reputation_log 
                WHERE agent_did = ? AND reason LIKE '%recovery%'
                ORDER BY log_id DESC LIMIT ?
            """, (agent_did, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_agent_weights(self) -> List[Dict]:
        """Get current weights for all agents."""
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT did, role, influence_weight, status FROM agent_registry
            """)
            
            return [dict(row) for row in cursor.fetchall()]


# =============================================================================
# Demo
# =============================================================================

def run_p2_demo():
    """Demonstrate P2 features."""
    print("\n" + "="*60)
    print("Q-DNA P2 FEATURES DEMONSTRATION")
    print("="*60)
    
    # 1. Deferral Windows
    print("\n⏱️ Deferral Windows")
    print("-" * 40)
    
    defer_mgr = DeferralManager()
    
    for cat in [DeferralCategory.SAFETY_CRITICAL, DeferralCategory.FINANCIAL, 
                DeferralCategory.REPUTATIONAL, DeferralCategory.LOW_RISK]:
        req = defer_mgr.request_deferral(
            f"artifact_{cat.name}",
            cat,
            f"Test deferral for {cat.name}"
        )
        hours = (req.max_end_time - req.start_time) / 3600
        print(f"  {cat.name}: Max {hours:.0f}h deferral → Status: {req.status}")
    
    # 2. Operational Mode Enforcement
    print("\n🔧 Operational Mode Enforcement")
    print("-" * 40)
    
    enforcer = ModeEnforcer()
    stats = enforcer.get_mode_stats()
    print(f"  Current Mode: {stats['current_mode']}")
    print(f"  L1 Behavior: {stats['l1_behavior']}")
    print(f"  L3 Behavior: {stats['l3_behavior']}")
    
    for grade in ["L1", "L2", "L3"]:
        should, reason = enforcer.should_verify(grade)
        status = "✓" if should else "✗"
        print(f"  {grade}: {status} - {reason}")
    
    # 3. Calibration Tracking
    print("\n📊 Calibration Error Tracking (Brier Score)")
    print("-" * 40)
    
    cal_tracker = CalibrationTracker()
    test_did = "did:myth:sentinel:test"
    
    # Simulate predictions
    predictions = [
        (0.9, True),   # High confidence, correct
        (0.8, True),   # Good calibration
        (0.95, False), # Overconfident - wrong
        (0.7, True),   # Reasonable
        (0.6, False),  # Underconfident
    ]
    
    for conf, correct in predictions:
        cal_tracker.record_prediction(test_did, conf, correct)
    
    report = cal_tracker.get_calibration_report(test_did)
    print(f"  Brier Score: {report['brier_score']}")
    print(f"  Accuracy: {report['accuracy']}")
    print(f"  Avg Confidence: {report['average_confidence']}")
    print(f"  Status: {report['calibration_status']}")
    
    # 4. Reputation Recovery
    print("\n📈 Reputation Auto-Recovery")
    print("-" * 40)
    
    recovery = ReputationRecovery()
    
    # Get all agents
    agents = recovery.get_all_agent_weights()
    for agent in agents[:2]:
        result = recovery.record_clean_audit(agent["did"])
        if "error" not in result:
            print(f"  {agent['role']}: {result['old_weight']:.2f} → {result['new_weight']:.2f}")
    
    print("\n✨ P2 Demo Complete")


if __name__ == "__main__":
    run_p2_demo()
