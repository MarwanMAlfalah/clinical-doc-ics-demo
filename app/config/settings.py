import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-70b-8192")

    # ASR
    ASR_MODEL_SIZE: str = os.getenv("ASR_MODEL_SIZE", "small")  # tiny, base, small, medium, large-v3
    ASR_DEVICE: str = os.getenv("ASR_DEVICE", "cpu")            # cpu or cuda (if you have GPU setup)
    ASR_COMPUTE_TYPE: str = os.getenv("ASR_COMPUTE_TYPE", "int8")  # int8 works well on CPU
