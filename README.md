# 🏥 Clinical Documentation ICS Demo
### Intelligent Control System for Automated Clinical Documentation
**(ASR + Groq LLaMA + Multi-Agent Control)**

---

## 📌 Overview

This repository presents a research-oriented software prototype that implements an
**Intelligent Control System (ICS)** for automated clinical documentation.

The system processes doctor–patient conversations and produces structured
**SOAP clinical notes** using a **multi-agent architecture** with explicit control logic,
supervision, and state transitions.

This project is designed as an academic research demo aligned with:
- Intelligent Control Systems (ICS)
- Multi-Agent Systems (MAS)
- Large Language Models (LLMs)
- Human-in-the-loop AI for healthcare

---

## 🧠 System Architecture

The system follows a closed-loop control pipeline:

Audio → ASR → LLM → Standardizer → Supervisor → Final Output  
             ↑_____________________________________↓  
                     Feedback & Control

### Core Agents

- **ASR Agent**  
  Converts audio to text using Whisper (faster-whisper).

- **LLM Agent**  
  Generates structured SOAP notes using Groq LLaMA.

- **Standardizer Agent**  
  Maps free text to canonical medical entities using an ontology.

- **Supervisor Agent**  
  Performs safety, quality, and consistency checks.

- **Control Core**  
  Manages state transitions, decisions, and logging.

---

## 🔁 Intelligent Control Model (ICS)

The system is modeled as a finite-state intelligent control system.

### States
- S0 – Start
- S_ASR – Speech recognition
- S_LLM – Clinical note generation
- S_STD – Ontology-based standardization
- S_SUP – Supervision and decision
- S_final – Final approved output

### Control Features
- Explicit state transition log
- Supervisor decision (APPROVE / HUMAN_REVIEW)
- Manual override: Force Human Review
- Full traceability for research and auditing

---

## 🎙️ Input Modes

### 1) Upload Audio (Offline Mode)
- Upload WAV, MP3, or M4A files
- Run the complete ICS pipeline

### 2) Live Recording (Near-Real-Time Mode)
- Record audio directly from the microphone (WebRTC)
- Save the recording as WAV
- Process using the same ICS pipeline
- Designed for future real-time extensions

---

## 🗂️ Project Structure

clinical-doc-ics-demo/
├── app/
│   ├── agents/
│   │   ├── asr_agent.py            # Whisper ASR agent
│   │   ├── llm_agent_groq.py       # Groq LLaMA agent
│   │   ├── standardizer_agent.py   # Ontology mapping
│   │   └── supervisor_agent.py     # Safety & quality control
│   │
│   ├── core/
│   │   ├── pipeline.py             # ICS pipeline orchestration
│   │   ├── state_machine.py        # State definitions & transitions
│   │   └── diagrams.py             # State diagram generation
│   │
│   ├── config/
│   │   └── settings.py             # Environment & model settings
│   │
│   ├── ui/
│   │   ├── main.py                 # Streamlit user interface
│   │   └── live_recorder.py        # Live microphone recording
│   │
│   └── kb/
│       └── ontology.json           # Medical entity mappings
│
├── docs/                           # Research documentation
├── tests/                          # Optional unit tests
├── requirements.txt
├── .env.example
├── LICENSE
└── README.md

---

## 🚀 Quick Start

### 1) Create a virtual environment

python -m venv .venv

Activate:

Windows:
.venv\Scripts\activate

Linux / macOS:
source .venv/bin/activate

---

### 2) Install dependencies

pip install -r requirements.txt

---

## 🎧 ASR Configuration (Whisper)

This demo uses faster-whisper for efficient local speech recognition.

Environment variables:

ASR_MODEL_SIZE=small        # tiny | base | small | medium  
ASR_DEVICE=cpu              # cpu | cuda  
ASR_COMPUTE_TYPE=int8       # int8 | float16  

Optimized for CPU execution on Windows by default.

---

## 🤖 LLM Configuration (Groq)

Create a .env file:

GROQ_API_KEY=your_api_key_here  
LLM_MODEL=llama-3.1-8b-instant  

Important:
This system does not perform autonomous medical diagnosis.
All outputs are assistive clinical documentation and must be reviewed by a clinician.

---

## ▶️ Run the Application

streamlit run app/ui/main.py

Open in browser:
http://localhost:8501

---

## 🧪 Example Outputs

- Full ASR transcript with timestamps
- Structured SOAP clinical note
- Normalized medical entities
- Supervisor decision (APPROVE / HUMAN_REVIEW)
- State transition log

---

## 🔐 Safety & Ethics

- Human-in-the-loop supervision
- Explicit supervisor control agent
- Manual override support
- No automated diagnosis
- Research and educational use only

---

## 🎓 Research Context

This project supports research in:
- Intelligent Control Systems
- Multi-Agent LLM Architectures
- Knowledge-based supervision
- Explainable AI for healthcare
- Human–AI collaboration

---

## 📄 License

MIT License  
Free to use for research and educational purposes.

---

## ✨ Author

Marwan M. Alfalah  
MSc Research Project for NuroScience module
Intelligent Systems & Artificial Intelligence

---

## 🧭 Future Work

- Streaming ASR with incremental SOAP updates
- Expanded medical knowledge graphs (SNOMED / ICD)
- Reinforcement-learning-based supervisor policies
- PDF / EHR export
- FastAPI backend for production deployment
