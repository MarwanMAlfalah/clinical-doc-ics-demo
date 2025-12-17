from dotenv import load_dotenv
load_dotenv()

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()  # loads .env from project root

@dataclass(frozen=True)
class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-70b-8192")

    ASR_MODEL_SIZE: str = os.getenv("ASR_MODEL_SIZE", "small")
    ASR_DEVICE: str = os.getenv("ASR_DEVICE", "cpu")
    ASR_COMPUTE_TYPE: str = os.getenv("ASR_COMPUTE_TYPE", "int8")
