import tempfile
import streamlit as st
import pandas as pd


from app.config.settings import Settings
from app.core.pipeline import ClinicalDocPipeline
from app.core.diagrams import build_state_diagram

force_human = st.checkbox("Force Human Review (manual override)", value=False)
st.set_page_config(page_title="Clinical Doc ICS Demo", layout="wide")
st.title("Clinical Documentation ICS Demo")
st.caption("(ICS): Audio → ASR → LLM → Standardizer → Supervisor → Final + State Log")
st.subheader("ICS State Diagram")
st.graphviz_chart(build_state_diagram())


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
            out = pipeline.run_full(audio_path, force_human_review=force_human)

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

        st.subheader("State Transition Log")

        log_df = pd.DataFrame(out.meta["state_log"])
        st.dataframe(log_df, use_container_width=True)

        st.json(out.meta["state_log"])
