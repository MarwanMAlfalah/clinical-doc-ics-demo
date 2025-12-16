from dataclasses import dataclass
from typing import Optional, Dict, Any

from app.config.settings import Settings
from app.agents.asr_agent import ASRAgent, ASRResult


@dataclass
class PipelineOutput:
    asr: ASRResult
    meta: Dict[str, Any]


class ClinicalDocPipeline:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.asr_agent = ASRAgent(
            model_size=settings.ASR_MODEL_SIZE,
            device=settings.ASR_DEVICE,
            compute_type=settings.ASR_COMPUTE_TYPE,
        )

    def run_asr_only(self, audio_path: str) -> PipelineOutput:
        asr_result = self.asr_agent.transcribe(audio_path=audio_path, language="en")
        meta = {
            "stage": "ASR_DONE",
            "asr_model": self.settings.ASR_MODEL_SIZE,
            "device": self.settings.ASR_DEVICE
        }
        return PipelineOutput(asr=asr_result, meta=meta)
