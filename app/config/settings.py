# app/config/settings.py
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    # Groq
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama3-70b-8192")

    # ASR (faster-whisper)
    asr_model_size: str = os.getenv("ASR_MODEL_SIZE", "small")
    asr_device: str = os.getenv("ASR_DEVICE", "cpu")
    asr_compute_type: str = os.getenv("ASR_COMPUTE_TYPE", "int8")
