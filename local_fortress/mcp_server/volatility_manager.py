"""
QoreLogic Volatility & SLA Manager

Implements:
- Volatility TTL tracking for claims
- SLA enforcement for L3 verification (< 24 hours)
- Expiration monitoring and alerts
"""

import sqlite3
import time
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "ledger" / "qorelogic_soa_ledger.db"


class VolatilityClass(Enum):
    """Volatility classes with their TTL in seconds."""
    REAL_TIME = 300           # 5 minutes - live data
    FINANCIAL = 86400         # 24 hours
    LEADERSHIP = 86400        # 24 hours
    REGULATORY = 604800       # 7 days
    CODE = 2592000            # 30 days
    DOCUMENTATION = 7776000   # 90 days
    STABLE = 31536000         # 1 year


@dataclass
class TrackedClaim:
    """A claim with volatility tracking."""
    claim_id: str
    content_hash: str
    source_url: Optional[str]
    volatility_class: str
    created_at: float
    ttl_seconds: int
    expires_at: float
    last_verified_at: float
    verification_count: int
    
    def is_expired(self) -> bool:
        return time.time() > self.expires_at
    
    def is_stale(self) -> bool:
        """Check if claim needs re-verification (50% of TTL)."""
        halfway = self.created_at + (self.ttl_seconds / 2)
        return time.time() > halfway and self.last_verified_at < halfway


@dataclass
class L3Request:
    """An L3 verification request with SLA tracking."""
    request_id: int
    artifact_hash: str
    agent_did: str
    created_at: float
    sla_deadline: float  # 24 hours from creation
    status: str
    approved_at: Optional[float]
    
    def is_overdue(self) -> bool:
        return self.status == "PENDING" and time.time() > self.sla_deadline
    
    def time_remaining(self) -> float:
        """Seconds remaining until SLA breach."""
        return max(0, self.sla_deadline - time.time())


class VolatilityManager:
    """Manages TTL tracking for claims and citations."""
    
    def __init__(self):
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Ensure the volatility tracking table exists."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS claim_volatility (
                claim_id TEXT PRIMARY KEY,
                content_hash TEXT NOT NULL,
                source_url TEXT,
                volatility_class TEXT NOT NULL,
                created_at REAL NOT NULL,
                ttl_seconds INTEGER NOT NULL,
                expires_at REAL NOT NULL,
                last_verified_at REAL NOT NULL,
                verification_count INTEGER DEFAULT 1
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_volatility_expires 
            ON claim_volatility(expires_at)
        """)
        
        conn.commit()
        conn.close()
    
    def register_claim(
        self, 
        content: str, 
        volatility_class: VolatilityClass,
        source_url: str = None
    ) -> TrackedClaim:
        """
        Register a new claim with volatility tracking.
        
        Args:
            content: The claim content
            volatility_class: The volatility category
            source_url: Optional source URL
            
        Returns:
            TrackedClaim object
        """
        import hashlib
        
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        claim_id = f"claim_{content_hash}_{int(time.time())}"
        
        now = time.time()
        ttl = volatility_class.value
        
        claim = TrackedClaim(
            claim_id=claim_id,
            content_hash=content_hash,
            source_url=source_url,
            volatility_class=volatility_class.name,
            created_at=now,
            ttl_seconds=ttl,
            expires_at=now + ttl,
            last_verified_at=now,
            verification_count=1
        )
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO claim_volatility 
            (claim_id, content_hash, source_url, volatility_class, 
             created_at, ttl_seconds, expires_at, last_verified_at, verification_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            claim.claim_id, claim.content_hash, claim.source_url,
            claim.volatility_class, claim.created_at, claim.ttl_seconds,
            claim.expires_at, claim.last_verified_at, claim.verification_count
        ))
        
        conn.commit()
        conn.close()
        
        return claim
    
    def refresh_claim(self, claim_id: str) -> Optional[TrackedClaim]:
        """
        Refresh a claim's TTL after re-verification.
        
        Args:
            claim_id: The claim to refresh
            
        Returns:
            Updated TrackedClaim or None if not found
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM claim_volatility WHERE claim_id = ?", (claim_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        now = time.time()
        new_expires = now + row[5]  # ttl_seconds
        new_count = row[8] + 1
        
        cursor.execute("""
            UPDATE claim_volatility 
            SET expires_at = ?, last_verified_at = ?, verification_count = ?
            WHERE claim_id = ?
        """, (new_expires, now, new_count, claim_id))
        
        conn.commit()
        conn.close()
        
        return TrackedClaim(
            claim_id=row[0],
            content_hash=row[1],
            source_url=row[2],
            volatility_class=row[3],
            created_at=row[4],
            ttl_seconds=row[5],
            expires_at=new_expires,
            last_verified_at=now,
            verification_count=new_count
        )
    
    def get_expired_claims(self) -> List[TrackedClaim]:
        """Get all expired claims that need re-verification."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM claim_volatility 
            WHERE expires_at < ?
            ORDER BY expires_at ASC
        """, (time.time(),))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [TrackedClaim(*row) for row in rows]
    
    def get_stale_claims(self) -> List[TrackedClaim]:
        """Get claims that are past 50% of their TTL (recommended re-verify)."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        now = time.time()
        
        cursor.execute("""
            SELECT * FROM claim_volatility 
            WHERE (created_at + ttl_seconds / 2) < ?
            AND last_verified_at < (created_at + ttl_seconds / 2)
            ORDER BY expires_at ASC
        """, (now,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [TrackedClaim(*row) for row in rows]


class SLAManager:
    """Manages SLA enforcement for L3 verification."""
    
    L3_SLA_SECONDS = 24 * 60 * 60  # 24 hours
    
    def __init__(self):
        pass  # Uses existing l3_approval_queue table
    
    def get_pending_requests(self) -> List[L3Request]:
        """Get all pending L3 requests."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT queue_id, artifact_hash, requesting_agent, timestamp, status
            FROM l3_approval_queue 
            WHERE status = 'PENDING'
            ORDER BY timestamp ASC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        requests = []
        for row in rows:
            created_at = self._parse_timestamp(row["timestamp"])
            requests.append(L3Request(
                request_id=row["queue_id"],
                artifact_hash=row["artifact_hash"],
                agent_did=row["requesting_agent"],
                created_at=created_at,
                sla_deadline=created_at + self.L3_SLA_SECONDS,
                status=row["status"],
                approved_at=None
            ))
        
        return requests
    
    def _parse_timestamp(self, ts) -> float:
        """Parse SQLite timestamp to epoch."""
        if isinstance(ts, (int, float)):
            return float(ts)
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            return dt.timestamp()
        except:
            return time.time()
    
    def get_overdue_requests(self) -> List[L3Request]:
        """Get L3 requests that have breached SLA."""
        all_pending = self.get_pending_requests()
        return [r for r in all_pending if r.is_overdue()]
    
    def get_sla_status(self) -> Dict:
        """Get overall SLA compliance status."""
        pending = self.get_pending_requests()
        overdue = [r for r in pending if r.is_overdue()]
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Count completed within SLA
        cursor.execute("""
            SELECT COUNT(*) FROM l3_approval_queue 
            WHERE status IN ('APPROVED', 'REJECTED')
        """)
        completed = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "pending_count": len(pending),
            "overdue_count": len(overdue),
            "completed_count": completed,
            "sla_compliance_pct": 100.0 if len(overdue) == 0 else 
                                  ((len(pending) - len(overdue)) / len(pending) * 100) if pending else 100.0,
            "oldest_pending": min((r.created_at for r in pending), default=None),
            "next_deadline": min((r.sla_deadline for r in pending), default=None)
        }
    
    def escalate_overdue(self) -> List[Dict]:
        """
        Escalate overdue L3 requests.
        Returns list of escalation notices.
        """
        overdue = self.get_overdue_requests()
        notices = []
        
        for req in overdue:
            hours_overdue = (time.time() - req.sla_deadline) / 3600
            notices.append({
                "request_id": req.request_id,
                "artifact_hash": req.artifact_hash,
                "hours_overdue": round(hours_overdue, 2),
                "severity": "CRITICAL" if hours_overdue > 12 else "WARNING",
                "action": "IMMEDIATE_ATTENTION_REQUIRED"
            })
        
        return notices


def run_health_check():
    """Run a health check on volatility and SLA status."""
    print("\n" + "=" * 60)
    print("QoreLogic VOLATILITY & SLA HEALTH CHECK")
    print("=" * 60)
    
    vol_mgr = VolatilityManager()
    sla_mgr = SLAManager()
    
    # Volatility Status
    expired = vol_mgr.get_expired_claims()
    stale = vol_mgr.get_stale_claims()
    
    print(f"\n📋 Claim Volatility Status:")
    print(f"   Expired claims: {len(expired)}")
    print(f"   Stale claims (need refresh): {len(stale)}")
    
    if expired:
        print(f"\n   ⚠️ Expired Claims:")
        for claim in expired[:5]:
            hours_expired = (time.time() - claim.expires_at) / 3600
            print(f"      - {claim.claim_id}: {hours_expired:.1f}h overdue")
    
    # SLA Status
    sla_status = sla_mgr.get_sla_status()
    
    print(f"\n⏱️ L3 SLA Status:")
    print(f"   Pending approvals: {sla_status['pending_count']}")
    print(f"   Overdue (SLA breach): {sla_status['overdue_count']}")
    print(f"   Completed: {sla_status['completed_count']}")
    print(f"   SLA Compliance: {sla_status['sla_compliance_pct']:.1f}%")
    
    if sla_status['next_deadline']:
        remaining = sla_status['next_deadline'] - time.time()
        hours = remaining / 3600
        print(f"   Next deadline in: {hours:.1f} hours")
    
    # Escalations
    escalations = sla_mgr.escalate_overdue()
    if escalations:
        print(f"\n🚨 SLA ESCALATIONS:")
        for esc in escalations:
            print(f"   [{esc['severity']}] Request {esc['request_id']}: "
                  f"{esc['hours_overdue']}h overdue")
    
    print("\n" + "=" * 60)
    
    return {
        "volatility": {"expired": len(expired), "stale": len(stale)},
        "sla": sla_status
    }


if __name__ == "__main__":
    run_health_check()
