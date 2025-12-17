from dataclasses import dataclass
from typing import Dict, Any
from app.agents.asr_agent import ASRResult

@dataclass
class PipelineOutput:
    asr: ASRResult
    soap_note: str
    meta: Dict[str, Any]


from app.config.settings import Settings
from app.agents.asr_agent import ASRAgent, ASRResult
from app.agents.llm_agent_groq import GroqLLMAgent


class ClinicalDocPipeline:
    def __init__(self, settings: Settings):
        self.settings = settings

        self.asr_agent = ASRAgent(
            model_size=settings.ASR_MODEL_SIZE,
            device=settings.ASR_DEVICE,
            compute_type=settings.ASR_COMPUTE_TYPE,
        )

        self.llm_agent = GroqLLMAgent(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL
        )

    def run_asr_to_soap(self, audio_path: str) -> PipelineOutput:
        # 1) ASR
        asr_result = self.asr_agent.transcribe(audio_path=audio_path, language="en")

        # 2) LLM SOAP note
        soap_note = self.llm_agent.generate_soap(asr_result.text)


        meta = {
            "stage": "LLM_DONE",
            "asr_model": self.settings.ASR_MODEL_SIZE,
            "llm_model": self.settings.GROQ_MODEL,
            "state_transition": ["S_ASR", "S_LLM"]
        }

        return PipelineOutput(asr=asr_result, soap_note=soap_note, meta=meta)

