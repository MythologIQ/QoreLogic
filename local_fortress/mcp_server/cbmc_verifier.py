"""
Q-DNA CBMC Verifier Module

Phase 9: Real Bounded Model Checking Integration
Spec Reference: §3.3.3 (Tier 3 Formal Verification)
Research: FORMAL_METHODS.md - BMC, Small Scope Hypothesis

Provides integration with CBMC (C Bounded Model Checker) for
Tier 3 formal verification. Gracefully degrades to heuristic
checks when CBMC is not available.

Key Parameters (from research):
- --unwind 10: Small Scope Hypothesis covers 5-10 steps
- --depth 100: Limit instruction depth for performance
"""

import subprocess
import tempfile
import os
import re
import json
from typing import Optional, List, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum
import logging


class CBMCStatus(Enum):
    """CBMC verification result status."""
    PASS = "PASS"              # No violations found (within bound)
    FAIL = "FAIL"              # Counterexample found
    UNAVAILABLE = "UNAVAILABLE"  # CBMC not installed
    TIMEOUT = "TIMEOUT"        # Verification timed out
    ERROR = "ERROR"            # Tool execution error


@dataclass
class CBMCResult:
    """Result from CBMC verification."""
    status: CBMCStatus
    bound: int
    violations: List[str]
    counterexample: Optional[str]
    latency_ms: float
    raw_output: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "bound": self.bound,
            "violations": self.violations,
            "counterexample": self.counterexample,
            "latency_ms": round(self.latency_ms, 2)
        }


class CBMCVerifier:
    """
    Bounded Model Checking integration for Q-DNA Sentinel.
    
    Uses CBMC to verify C code or transpiled Python-to-C code.
    Falls back to heuristic checks when CBMC is unavailable.
    
    Per FORMAL_METHODS.md:
    - Small Scope Hypothesis: 5-10 steps catch most bugs
    - Default unwind bound: 10
    - Default depth limit: 100
    """
    
    # Default BMC parameters (from FORMAL_METHODS.md research)
    DEFAULT_UNWIND = 10       # Loop unrolling bound
    DEFAULT_DEPTH = 100       # Instruction depth limit
    DEFAULT_TIMEOUT = 30      # Seconds
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._cbmc_path: Optional[str] = None
        self._cbmc_available: Optional[bool] = None
    
    @property
    def cbmc_available(self) -> bool:
        """Check if CBMC is available in PATH."""
        if self._cbmc_available is None:
            self._cbmc_available = self._check_cbmc()
        return self._cbmc_available
    
    def _check_cbmc(self) -> bool:
        """Probe for CBMC installation."""
        try:
            result = subprocess.run(
                ["cbmc", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                self.logger.info(f"CBMC found: {version}")
                self._cbmc_path = "cbmc"
                return True
        except FileNotFoundError:
            self.logger.warning("CBMC not found in PATH")
        except subprocess.TimeoutExpired:
            self.logger.warning("CBMC version check timed out")
        except Exception as e:
            self.logger.warning(f"CBMC check failed: {e}")
        
        return False
    
    def verify_c_code(
        self,
        c_code: str,
        unwind: int = DEFAULT_UNWIND,
        depth: int = DEFAULT_DEPTH,
        timeout: int = DEFAULT_TIMEOUT,
        properties: Optional[List[str]] = None
    ) -> CBMCResult:
        """
        Verify C code using CBMC bounded model checker.
        
        Args:
            c_code: C source code to verify
            unwind: Loop unrolling bound (default: 10 per Small Scope Hypothesis)
            depth: Instruction depth limit
            timeout: Verification timeout in seconds
            properties: Optional list of specific properties to check
            
        Returns:
            CBMCResult with verification status
        """
        import time
        start_time = time.perf_counter()
        
        if not self.cbmc_available:
            return CBMCResult(
                status=CBMCStatus.UNAVAILABLE,
                bound=unwind,
                violations=["CBMC not installed - using heuristic fallback"],
                counterexample=None,
                latency_ms=(time.perf_counter() - start_time) * 1000
            )
        
        # Write C code to temp file
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.c', delete=False, encoding='utf-8'
        ) as tmp:
            tmp.write(c_code)
            tmp_path = tmp.name
        
        try:
            # Build CBMC command
            cmd = [
                "cbmc",
                tmp_path,
                f"--unwind", str(unwind),
                f"--depth", str(depth),
                "--bounds-check",          # Check array bounds
                "--pointer-check",         # Check pointer safety
                "--div-by-zero-check",     # Check division by zero
                "--signed-overflow-check", # Check integer overflow
                "--json-ui"                # JSON output for parsing
            ]
            
            if properties:
                for prop in properties:
                    cmd.extend(["--property", prop])
            
            # Run CBMC
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            latency = (time.perf_counter() - start_time) * 1000
            
            # Parse JSON output
            violations = []
            counterexample = None
            
            try:
                # CBMC JSON output is an array of objects
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines:
                    if line.startswith('[') or line.startswith('{'):
                        try:
                            data = json.loads(line)
                            violations.extend(self._parse_cbmc_json(data))
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                self.logger.warning(f"Failed to parse CBMC JSON: {e}")
                # Fall back to text parsing
                violations = self._parse_cbmc_text(result.stdout)
            
            # Determine status
            if result.returncode == 0:
                status = CBMCStatus.PASS
            elif result.returncode == 10:  # CBMC uses 10 for verification failure
                status = CBMCStatus.FAIL
                counterexample = self._extract_counterexample(result.stdout)
            else:
                status = CBMCStatus.ERROR
                violations.append(f"CBMC returned code {result.returncode}")
            
            return CBMCResult(
                status=status,
                bound=unwind,
                violations=violations,
                counterexample=counterexample,
                latency_ms=latency,
                raw_output=result.stdout[:2000] if result.stdout else None
            )
            
        except subprocess.TimeoutExpired:
            return CBMCResult(
                status=CBMCStatus.TIMEOUT,
                bound=unwind,
                violations=[f"Verification timed out after {timeout}s"],
                counterexample=None,
                latency_ms=(time.perf_counter() - start_time) * 1000
            )
        except Exception as e:
            return CBMCResult(
                status=CBMCStatus.ERROR,
                bound=unwind,
                violations=[f"CBMC execution error: {str(e)}"],
                counterexample=None,
                latency_ms=(time.perf_counter() - start_time) * 1000
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def _parse_cbmc_json(self, data: Any) -> List[str]:
        """Parse CBMC JSON output for violations."""
        violations = []
        
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    if item.get("messageType") == "ERROR":
                        violations.append(item.get("messageText", "Unknown error"))
                    elif item.get("status") == "FAILURE":
                        prop = item.get("property", "unknown")
                        violations.append(f"Property violation: {prop}")
        elif isinstance(data, dict):
            if data.get("result") == "FAILURE":
                for prop in data.get("properties", []):
                    if prop.get("status") == "FAILURE":
                        violations.append(f"Property violation: {prop.get('property', 'unknown')}")
        
        return violations
    
    def _parse_cbmc_text(self, output: str) -> List[str]:
        """Fallback text parsing for CBMC output."""
        violations = []
        
        # Look for failure patterns
        patterns = [
            r"FAILURE: (.+)",
            r"ASSERT failed: (.+)",
            r"bounds check: (.+)",
            r"pointer check: (.+)",
            r"division by zero in (.+)"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            violations.extend(matches)
        
        return violations
    
    def _extract_counterexample(self, output: str) -> Optional[str]:
        """Extract counterexample trace from CBMC output."""
        # Look for trace section
        trace_match = re.search(r"Trace for [\w.]+:(.+?)(?=\n\n|\Z)", output, re.DOTALL)
        if trace_match:
            return trace_match.group(1).strip()[:1000]  # Limit size
        return None
    
    def heuristic_verify(self, code: str) -> CBMCResult:
        """
        Heuristic verification fallback when CBMC is unavailable.
        
        Performs pattern-based checks for common vulnerabilities:
        - Division by zero
        - Buffer overflows
        - Null pointer dereference
        - Integer overflow
        """
        import time
        start_time = time.perf_counter()
        
        violations = []
        
        # 1. Division by zero
        div_zero_patterns = [
            r'/\s*0\b',
            r'/\s*\(\s*0\s*\)',
            r'%\s*0\b'
        ]
        for pattern in div_zero_patterns:
            if re.search(pattern, code):
                violations.append("HEURISTIC: Potential division by zero")
                break
        
        # 2. Buffer overflow indicators in C
        buffer_patterns = [
            r'strcpy\s*\(',        # Unsafe strcpy
            r'strcat\s*\(',        # Unsafe strcat
            r'gets\s*\(',          # Dangerous gets
            r'sprintf\s*\(',       # Unsafe sprintf
            r'\[\s*\d{4,}\s*\]'    # Very large array index
        ]
        for pattern in buffer_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                violations.append(f"HEURISTIC: Potential buffer overflow ({pattern})")
        
        # 3. Null pointer dereference
        null_patterns = [
            r'\*\s*NULL',
            r'NULL\s*->'
        ]
        for pattern in null_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                violations.append("HEURISTIC: Potential null pointer dereference")
                break
        
        # 4. Integer overflow
        overflow_patterns = [
            r'INT_MAX\s*\+',
            r'\+\s*INT_MAX',
            r'UINT_MAX\s*\+'
        ]
        for pattern in overflow_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                violations.append("HEURISTIC: Potential integer overflow")
                break
        
        status = CBMCStatus.FAIL if violations else CBMCStatus.PASS
        
        return CBMCResult(
            status=status,
            bound=0,  # Heuristic, no bound
            violations=violations if violations else ["HEURISTIC: No obvious violations detected"],
            counterexample=None,
            latency_ms=(time.perf_counter() - start_time) * 1000
        )
    
    def verify(
        self,
        code: str,
        is_c_code: bool = True,
        unwind: int = DEFAULT_UNWIND,
        depth: int = DEFAULT_DEPTH
    ) -> CBMCResult:
        """
        Main verification entry point.
        
        Uses CBMC if available, otherwise falls back to heuristics.
        
        Args:
            code: Code to verify (C or Python)
            is_c_code: True if code is C, False for Python
            unwind: Loop unrolling bound
            depth: Instruction depth limit
            
        Returns:
            CBMCResult with verification outcome
        """
        if not is_c_code:
            # For Python, use heuristics only (PyVeritas transpilation is Phase 10+)
            return self.heuristic_verify(code)
        
        if self.cbmc_available:
            return self.verify_c_code(code, unwind, depth)
        else:
            return self.heuristic_verify(code)


# Global verifier instance
_verifier: Optional[CBMCVerifier] = None


def get_cbmc_verifier() -> CBMCVerifier:
    """Get or create the global CBMC verifier instance."""
    global _verifier
    if _verifier is None:
        _verifier = CBMCVerifier()
    return _verifier


# Quick helper for sentinel integration
def verify_code(code: str, is_c: bool = True) -> CBMCResult:
    """
    Quick helper to verify code with CBMC.
    
    Returns:
        CBMCResult with verification status
    """
    return get_cbmc_verifier().verify(code, is_c)


if __name__ == "__main__":
    # Test the verifier
    verifier = CBMCVerifier()
    
    print(f"CBMC Available: {verifier.cbmc_available}")
    
    # Test with sample C code containing a bug
    buggy_c = """
    int main() {
        int x = 10;
        int y = 0;
        int z = x / y;  // Division by zero!
        return z;
    }
    """
    
    result = verifier.verify(buggy_c, is_c_code=True)
    print(f"Verification result: {result.to_dict()}")
    
    # Test with safe code
    safe_c = """
    int main() {
        int x = 10;
        int y = 5;
        int z = x / y;
        return z;
    }
    """
    
    result = verifier.verify(safe_c, is_c_code=True)
    print(f"Safe code result: {result.to_dict()}")
