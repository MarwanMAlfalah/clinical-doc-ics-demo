import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # points to project root
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import os
import tempfile
import streamlit as st
from app.config.settings import Settings
from app.core.pipeline import ClinicalDocPipeline

st.set_page_config(page_title="Clinical Doc ICS Demo", layout="wide")

st.title("Clinical Documentation ICS Demo")
st.caption("Step 1 (MVP): Audio Upload → ASR Transcript")

settings = Settings()
pipeline = ClinicalDocPipeline(settings)

with st.container(border=True):
    uploaded = st.file_uploader("Upload an audio file (wav/mp3/m4a)", type=["wav", "mp3", "m4a"])


if uploaded:
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded.name).suffix) as tmp:
        tmp.write(uploaded.read())
        audio_path = tmp.name

    st.audio(audio_path)

    if st.button("Run ASR (Whisper)"):
        with st.spinner("Transcribing..."):
            out = pipeline.run_asr_only(audio_path)

        st.success("ASR completed.")

        st.subheader("Transcript")
        st.write(out.asr.text)

        st.subheader("Segments")
        st.json(out.asr.segments)

        st.subheader("Meta")
        st.json(out.meta)

    # Optional cleanup (keep file during session if needed)
    # os.remove(audio_path)
