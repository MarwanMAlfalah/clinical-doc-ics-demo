import os
import tempfile
import streamlit as st

from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av

from app.config.settings import Settings
from app.core.pipeline import ClinicalDocPipeline
from app.core.diagrams import build_state_diagram
from app.ui.live_recorder import push_audio_frame, drain_audio_to_wav


st.set_page_config(page_title="Clinical Doc ICS Demo", layout="wide")
st.title("Clinical Documentation ICS Demo")
st.caption("(ICS): Audio → ASR → LLM → Standardizer → Supervisor → Final + State Log")

# Controls
force_human = st.checkbox("Force Human Review (manual override)", value=False)

st.subheader("ICS State Diagram")
st.graphviz_chart(build_state_diagram())

settings = Settings()
pipeline = ClinicalDocPipeline(settings)

tab_upload, tab_live = st.tabs(["Upload Audio (Existing)", "Live Recording (New)"])

with st.container(border=True):
    uploaded = st.file_uploader("Upload an audio file (wav/mp3/m4a)", type=["wav", "mp3", "m4a"])
    if uploaded:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded.name}") as tmp:
            tmp.write(uploaded.read())
            audio_path = tmp.name

        st.audio(audio_path)

        if st.button("Run Full ICS Pipeline", key="run_upload"):
            with st.spinner("Running full ICS pipeline..."):
                st.session_state["upload_out"] = pipeline.run_full(
                    audio_path,
                    force_human_review=force_human
                )

    # ✅ عرض النتائج فقط إذا كانت موجودة
    if "upload_out" in st.session_state:
        out = st.session_state["upload_out"]

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
        st.dataframe(pd.DataFrame(out.meta["state_log"]), use_container_width=True)


with tab_live:
    st.markdown("### Live Recording")
    st.write("Click **Start** to record from your microphone, then **Stop**, then run the pipeline on the recorded audio.")

    # WebRTC streamer
    def audio_frame_callback(frame: av.AudioFrame) -> av.AudioFrame:
        push_audio_frame(frame)
        return frame

    webrtc_streamer(
        key="live_recorder",
        mode=WebRtcMode.SENDONLY,
        audio_frame_callback=audio_frame_callback,
        media_stream_constraints={"audio": True, "video": False},
    )

    colA, colB = st.columns(2)

    with colA:
        if st.button("Save Recording to WAV", key="save_wav"):
            out_wav = os.path.join(tempfile.gettempdir(), "clinical_live_recording.wav")
            n = drain_audio_to_wav(out_wav, sample_rate=48000)

            if n == 0:
                st.error("No audio captured yet. Click Start and speak, then try again.")
            else:
                st.success(f"Saved: {out_wav} (samples: {n})")
                st.session_state["live_wav_path"] = out_wav
                st.audio(out_wav)

    with colB:
        if st.button("Run Pipeline on Live Recording", key="run_live"):
            wav_path = st.session_state.get("live_wav_path")
            if not wav_path or not os.path.exists(wav_path):
                st.error("Please record audio and click 'Save Recording to WAV' first.")
            else:
                with st.spinner("Running full ICS pipeline on live recording..."):
                    out = pipeline.run_full(wav_path, force_human_review=force_human)

                st.success(f"Done. Final decision: {out.sup.action}")
                # نفس عرض النتائج:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Transcript (ASR Output)")
                    st.write(out.asr.text)
                with col2:
                    st.subheader("SOAP Note (LLM Output)")
                    st.write(out.soap_note)

                st.subheader("Standardized Entities (Ontology Mapping)")
                st.json(out.std.entities)
                st.info(out.std.normalized_summary)

                st.subheader("Supervisor Decision")
                st.write(f"**Action:** {out.sup.action}")
                st.json(out.sup.reasons)

                import pandas as pd
                st.subheader("State Transition Log")
                st.dataframe(pd.DataFrame(out.meta["state_log"]), use_container_width=True)
