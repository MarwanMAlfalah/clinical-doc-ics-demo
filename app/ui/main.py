import tempfile
import streamlit as st

from app.config.settings import Settings
from app.core.pipeline import ClinicalDocPipeline

st.set_page_config(page_title="Clinical Doc ICS Demo", layout="wide")
st.title("Clinical Documentation ICS Demo")
st.caption("Step 3 (MVP): Audio Upload → ASR Transcript → Groq LLaMA SOAP Note")

settings = Settings()
pipeline = ClinicalDocPipeline(settings)

with st.container(border=True):
    uploaded = st.file_uploader("Upload an audio file (wav/mp3/m4a)", type=["wav", "mp3", "m4a"])

if uploaded:
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded.name}") as tmp:
        tmp.write(uploaded.read())
        audio_path = tmp.name

    st.audio(audio_path)

    if st.button("Run ASR → SOAP Note (Groq LLaMA)"):
        with st.spinner("Running ASR..."):
            out = pipeline.run_asr_to_soap(audio_path)

        st.success("Done.")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Transcript (ASR Output)")
            st.write(out.asr.text)
            st.subheader("ASR Segments")
            st.json(out.asr.segments)

        with col2:
            st.subheader("SOAP Note (LLM Output)")
            st.write(out.soap_note)

        st.subheader("Meta / State Transition")
        st.json(out.meta)
