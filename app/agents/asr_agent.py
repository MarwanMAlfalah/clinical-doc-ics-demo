from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from faster_whisper import WhisperModel


@dataclass
class ASRResult:
    text: str
    language: Optional[str]
    segments: List[Dict[str, Any]]
    avg_logprob: Optional[float]
    no_speech_prob: Optional[float]


class ASRAgent:
    """
    ASR Agent using faster-whisper.
    Converts audio -> transcript + basic confidence signals.
    """

    def __init__(self, model_size: str = "small", device: str = "cpu", compute_type: str = "int8"):
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(self, audio_path: str, language: Optional[str] = "en") -> ASRResult:
        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            vad_filter=True,
            beam_size=5
        )

        seg_list = []
        texts = []
        avg_logprob_vals = []
        no_speech_vals = []

        for seg in segments:
            seg_list.append({
                "start": float(seg.start),
                "end": float(seg.end),
                "text": seg.text.strip()
            })
            texts.append(seg.text.strip())

            # These fields may exist depending on build/version; keep safe:
            if getattr(seg, "avg_logprob", None) is not None:
                avg_logprob_vals.append(float(seg.avg_logprob))
            if getattr(seg, "no_speech_prob", None) is not None:
                no_speech_vals.append(float(seg.no_speech_prob))

        return ASRResult(
            text=" ".join([t for t in texts if t]),
            language=getattr(info, "language", None),
            segments=seg_list,
            avg_logprob=(sum(avg_logprob_vals) / len(avg_logprob_vals)) if avg_logprob_vals else None,
            no_speech_prob=(sum(no_speech_vals) / len(no_speech_vals)) if no_speech_vals else None,
        )
