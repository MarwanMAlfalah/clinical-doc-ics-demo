from dataclasses import dataclass
from typing import Dict, Any

from app.config.settings import Settings
from app.agents.asr_agent import ASRAgent, ASRResult
from app.agents.llm_agent_groq import GroqLLMAgent
from app.agents.standardizer_agent import StandardizerAgent, StandardizationResult
from app.agents.supervisor_agent import SupervisorAgent, SupervisorDecision
from app.core.state_machine import StateMachine


@dataclass
class PipelineOutput:
    asr: ASRResult
    soap_note: str
    std: StandardizationResult
    sup: SupervisorDecision
    meta: Dict[str, Any]


class ClinicalDocPipeline:
    def __init__(self, settings: Settings):
        self.settings = settings

        self.asr_agent = ASRAgent(
            model_size=settings.asr_model_size,
            device=settings.asr_device,
            compute_type=settings.asr_compute_type,
        )

        self.llm_agent = GroqLLMAgent(
            api_key=settings.groq_api_key,
            model=settings.groq_model
        )


        self.std_agent = StandardizerAgent("app/kb/ontology_stub.json")
        self.sup_agent = SupervisorAgent(min_length=150)

    def run_full(self, audio_path: str, force_human_review: bool = False) -> PipelineOutput:
        sm = StateMachine()

        # ASR
        asr = self.asr_agent.transcribe(audio_path=audio_path, language="en")
        sm.transition("S_ASR", "u_asr", {"segments": len(asr.segments)})

        # LLM
        soap = self.llm_agent.generate_soap(asr.text)
        sm.transition("S_LLM", "u_llm", {"llm_model": self.settings.groq_model})

        # Standardizer
        std = self.std_agent.standardize(asr.text, soap)
        sm.transition("S_STD", "u_std", {"entities": {k: len(v) for k, v in std.entities.items()}})

        # Supervisor
        sup = self.sup_agent.decide(asr.text, soap)
        sm.transition("S_SUP", "u_sup", {"decision": sup.action, "reasons": sup.reasons})

        # Force Human Review (manual override)
        if force_human_review:
            sup.action = "HUMAN_REVIEW"
            sup.reasons["manual_override"] = True
            sup.reasons["override_reason"] = "Force Human Review enabled by user"
            sm.transition("S_SUP", "u_override", {"decision": sup.action, "reasons": sup.reasons})


        # Final
        sm.transition("S_final", "u_finalize", {"final": sup.action})

        meta = {
            "stage": "DONE",
            "asr_model": self.settings.asr_model_size,
            "llm_model": self.settings.groq_model,
            "final_decision": sup.action,
            "state_log": [e.__dict__ for e in sm.log]
        }

        return PipelineOutput(asr=asr, soap_note=soap, std=std, sup=sup, meta=meta)
