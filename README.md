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
