# Clinical Documentation ICS Demo (ASR + Groq LLaMA)

A minimal research demo that implements an Intelligent Control System (ICS) for automated clinical documentation using:
- ASR Agent (speech-to-text)
- LLM Agent (Groq LLaMA via Groq API)
- Standardizer Agent (ontology-based mapping)
- Supervisor Agent (safety + quality checks)
- State Machine + Decision Log

## Quick Start
1) Create a virtual environment and install dependencies:
```bash
python -m venv .venv
# activate it...
pip install -r requirements.txt

## ASR (Whisper)
This demo uses `faster-whisper` for local speech-to-text on Windows.
By default it runs on CPU with int8 compute for good speed.

Environment variables:
- ASR_MODEL_SIZE (e.g., small)
- ASR_DEVICE (cpu/cuda)
- ASR_COMPUTE_TYPE (int8/float16)
