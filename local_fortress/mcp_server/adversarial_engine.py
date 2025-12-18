"""
Q-DNA Adversarial Engine (Phase 9 - Track P3)
Implements the 'Devil's Advocate' review mechanism for L3 artifacts.

Research: Adversarial Review [ML-003]
Spec: §7.3 (Constructive Dissent)

[L3] Logic frame for generating criticism prompts and parsing objections.
"""
import json
import logging
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, asdict

class ReviewPerspective(Enum):
    """The lens through which the adversary critiques."""
    SECURITY_PESSIMIST = "SECURITY_PESSIMIST"  # Assumes all inputs are malicious
    PERFORMANCE_SKEPTIC = "PERFORMANCE_SKEPTIC" # Assumes code will scale poorly
    COMPLIANCE_OFFICER = "COMPLIANCE_OFFICER"    # Pedantic adherence to spec
    CHAOS_MONKEY = "CHAOS_MONKEY"                # Focused on failure modes/crashes

@dataclass
class Objection:
    perspective: str
    severity: str # LOW, MEDIUM, CRITICAL
    claim: str
    counter_proof_required: bool

class AdversarialEngine:
    """
    Orchestrates the 'Adversarius' process.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate_challenge_prompt(self, content: str, perspective: ReviewPerspective) -> str:
        """
        Constructs the challenge prompt for the LLM based on perspective.
        """
        personas = {
            ReviewPerspective.SECURITY_PESSIMIST: 
                "You are a paranoid security researcher. Assume verify_trust() always fails and database is compromised. Find 3 vulnerabilities.",
            ReviewPerspective.PERFORMANCE_SKEPTIC:
                "You are a high-frequency trading engineer. Identify O(n^2) loops or blocking I/O that will hang the system under load.",
            ReviewPerspective.COMPLIANCE_OFFICER:
                "You are a GDPR auditor. Flag any strict PII violations or data residency issues per Article 22.",
            ReviewPerspective.CHAOS_MONKEY:
                "You are a chaos engineer. What happens if the network drops right after line 5? What if disk is full?"
        }
        
        base_instruction = personas.get(perspective, "Critique this code ruthlessly.")
        
        prompt = f"""
        *** ADVERSARIAL REVIEW REQUEST ***
        CONTEXT: Phase 9 Q-DNA Trusted System
        ROLE: {perspective.value}
        INSTRUCTION: {base_instruction}
        
        TARGET ARTIFACT:
        ```
        {content}
        ```
        
        OUTPUT FORMAT:
        Return a JSON list of objections:
        [
          {{ "severity": "CRITICAL", "claim": "...", "counter_proof_required": true }}
        ]
        """
        return prompt.strip()

    def parse_critique(self, response_text: str) -> List[Dict]:
        """
        Parses the JSON response from the adversary model.
        """
        try:
            # Attempt to find JSON structure in the response (robust to markdown backticks)
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON list found")
                
            json_str = response_text[start:end]
            data = json.loads(json_str)
            
            valid_objections = []
            for item in data:
                # Basic validation
                if "claim" in item and "severity" in item:
                    valid_objections.append(item)
            
            return valid_objections
            
        except Exception as e:
            self.logger.error(f"Failed to parse critique: {e}")
            return [{"severity": "ERROR", "claim": "Failed to parse adversary response", "raw": response_text[:100]}]

# Singleton
_adversarial_engine = AdversarialEngine()

def get_adversarial_engine() -> AdversarialEngine:
    return _adversarial_engine
