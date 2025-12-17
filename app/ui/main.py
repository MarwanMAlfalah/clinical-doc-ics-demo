import tempfile
import streamlit as st

from app.config.settings import Settings
from app.core.pipeline import ClinicalDocPipeline

st.set_page_config(page_title="Clinical Doc ICS Demo", layout="wide")
st.title("Clinical Documentation ICS Demo")
st.caption("Step 4 (ICS): Audio → ASR → LLM → Standardizer → Supervisor → Final + State Log")

settings = Settings()
pipeline = ClinicalDocPipeline(settings)

with st.container(border=True):
    uploaded = st.file_uploader("Upload an audio file (wav/mp3/m4a)", type=["wav", "mp3", "m4a"])

if uploaded:
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded.name}") as tmp:
        tmp.write(uploaded.read())
        audio_path = tmp.name

    st.audio(audio_path)

    if st.button("Run Full ICS Pipeline"):
        with st.spinner("Running full ICS pipeline..."):
            out = pipeline.run_full(audio_path)

        st.success(f"Done. Final decision: {out.sup.action}")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Transcript (ASR Output)")
            st.write(out.asr.text)
            st.subheader("ASR Segments")
            st.json(out.asr.segments)

        with col2:
            st.subheader("SOAP Note (LLM Output)")
            st.write(out.soap_note)

        st.subheader("Standardized Entities (Ontology Mapping)")
        st.json(out.std.entities)
        st.info(out.std.normalized_summary)

        st.subheader("Supervisor Decision")
        st.write(f"**Action:** {out.sup.action}")
        st.json(out.sup.reasons)

        st.subheader("State Transition Log (Part 4)")
        st.json(out.meta["state_log"])
