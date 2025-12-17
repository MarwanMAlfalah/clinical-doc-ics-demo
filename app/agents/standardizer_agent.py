import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any


@dataclass
class StandardizationResult:
    entities: Dict[str, List[Dict[str, Any]]]   # {"symptoms":[{...}], "medications":[...], "conditions":[...]}
    normalized_summary: str


class StandardizerAgent:
    """
    Simple ontology-based standardizer:
    - Extracts mentions from transcript and SOAP note
    - Maps to canonical ontology keys using substring matching
    """

    def __init__(self, ontology_path: str):
        self.ontology_path = ontology_path
        self.ontology = json.loads(Path(ontology_path).read_text(encoding="utf-8"))

    def _match_category(self, text: str, category: str) -> List[Dict[str, Any]]:
        text_l = text.lower()
        results = []
        for canonical, synonyms in self.ontology.get(category, {}).items():
            for s in synonyms:
                if s.lower() in text_l:
                    results.append({
                        "canonical": canonical,
                        "matched": s,
                        "category": category
                    })
                    break
        return results

    def standardize(self, transcript: str, soap_note: str) -> StandardizationResult:
        combined = f"{transcript}\n\n{soap_note}"
        symptoms = self._match_category(combined, "symptoms")
        meds = self._match_category(combined, "medications")
        conds = self._match_category(combined, "conditions")

        entities = {
            "symptoms": symptoms,
            "medications": meds,
            "conditions": conds
        }

        # A simple normalized summary (for demo)
        norm_sym = ", ".join(sorted({e["canonical"] for e in symptoms})) or "none"
        norm_med = ", ".join(sorted({e["canonical"] for e in meds})) or "none"
        norm_con = ", ".join(sorted({e["canonical"] for e in conds})) or "none"

        normalized_summary = (
            f"Normalized entities → symptoms: {norm_sym}; medications: {norm_med}; conditions: {norm_con}."
        )

        return StandardizationResult(entities=entities, normalized_summary=normalized_summary)
