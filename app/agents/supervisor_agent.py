from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class SupervisorDecision:
    action: str          # APPROVE | REGENERATE | HUMAN_REVIEW
    reasons: Dict[str, Any]
    final_note: str


class SupervisorAgent:
    """
    Simple supervisor:
    - Basic checks on SOAP note quality and safety
    - Decides: APPROVE / REGENERATE / HUMAN_REVIEW
    """

    def __init__(self,
                 min_length: int = 200,
                 max_length: int = 4000,
                 require_sections: bool = True):
        self.min_length = min_length
        self.max_length = max_length
        self.require_sections = require_sections

    def _has_sections(self, note: str) -> bool:
        required = ["S:", "O:", "A:", "P:"]
        return all(r in note for r in required)

    def decide(self, transcript: str, soap_note: str) -> SupervisorDecision:
        reasons = {}

        n = len(soap_note.strip())
        reasons["length"] = n

        if n < self.min_length:
            reasons["problem"] = "SOAP note too short"
            return SupervisorDecision("REGENERATE", reasons, soap_note)

        if n > self.max_length:
            reasons["problem"] = "SOAP note too long"
            return SupervisorDecision("REGENERATE", reasons, soap_note)

        if self.require_sections and not self._has_sections(soap_note):
            reasons["problem"] = "Missing SOAP sections (S/O/A/P)"
            return SupervisorDecision("REGENERATE", reasons, soap_note)

        # Simple hallucination guard: if note contains explicit uncertainty markers too much
        suspicious_markers = ["I assume", "maybe", "probably", "might be", "not sure"]
        hits = sum(1 for m in suspicious_markers if m.lower() in soap_note.lower())
        reasons["uncertainty_markers"] = hits
        if hits >= 3:
            reasons["problem"] = "Too many uncertainty markers"
            return SupervisorDecision("HUMAN_REVIEW", reasons, soap_note)

        # Basic approve
        reasons["status"] = "Passed basic checks"
        return SupervisorDecision("APPROVE", reasons, soap_note)
