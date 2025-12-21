"""
QoreLogic BMC Verifier (Phase 9)

Wrapper for CBMC (Bounded Model Checker).
Since PyVeritas (Python->C transpiler) is still experimental,
this module currently serves as the interface definition and
C-code verifier, returning UNAVAILABLE for raw Python unless
transpilation is active.
"""
import shutil
import subprocess
import tempfile
import os
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class CBMCStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"
    UNAVAILABLE = "UNAVAILABLE"

@dataclass
class BMCResult:
    status: CBMCStatus
    violations: List[str]
    output: str

class CBMCVerifier:
    def __init__(self):
        self.cbmc_path = shutil.which("cbmc")
        self.has_cbmc = self.cbmc_path is not None

    def verify(self, content: str, is_c_code: bool = False) -> BMCResult:
        """
        Run Bounded Model Checking on the artifact.
        
        Args:
            content: Source code
            is_c_code: True if content is C, False if Python
            
        Returns:
            BMCResult
        """
        if not is_c_code:
            # Phase 9: Python support requires PyVeritas transpiler.
            # Currently not integrated in this container.
            return BMCResult(
                status=CBMCStatus.UNAVAILABLE,
                violations=[],
                output="Python verification requires active PyVeritas transpiler."
            )

        if not self.has_cbmc:
             return BMCResult(
                status=CBMCStatus.UNAVAILABLE,
                violations=[],
                output="CBMC binary not found in PATH."
            )

        # Handle C Code Verification
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # Run CBMC: cbmc file.c --unwind 10 --bounds-check --pointer-check
            cmd = [
                self.cbmc_path, 
                tmp_path, 
                "--unwind", "10", 
                "--bounds-check", 
                "--pointer-check",
                "--div-by-zero-check"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return BMCResult(CBMCStatus.PASS, [], result.stdout)
            elif result.returncode == 10:
                # CBMC returns 10 for Verification Failed
                violations = self._parse_cbmc_output(result.stdout)
                return BMCResult(CBMCStatus.FAIL, violations, result.stdout)
            else:
                return BMCResult(CBMCStatus.ERROR, [], result.stderr)
                
        except Exception as e:
            return BMCResult(CBMCStatus.ERROR, [], str(e))
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def _parse_cbmc_output(self, output: str) -> List[str]:
        """Simple parser for CBMC text output."""
        violations = []
        for line in output.splitlines():
            if "FAILURE" in line:
                violations.append(line.strip())
        return violations

def get_cbmc_verifier() -> CBMCVerifier:
    return CBMCVerifier()
