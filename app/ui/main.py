import os
import pandas as pd
import tempfile
import streamlit as st
import time
import pandas as pd
from app.ui.streaming_asr import StreamingASRSession
from aiortc import RTCConfiguration, RTCIceServer

from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
from aiortc import RTCConfiguration, RTCIceServer

RTC_CONFIG = RTCConfiguration(
    iceServers=[RTCIceServer(urls=["stun:stun.l.google.com:19302"])]
)

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

tab_upload, tab_live, tab_stream = st.tabs([
    "Upload Audio (Existing)",
    "Live Recording (New)",
    "Live Streaming ASR (NEW)"
])

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

with tab_stream:
    st.markdown("### Live Streaming ASR (Chunk-based)")
    st.write("Start speaking. The transcript will update every few seconds.")

    # UI controls
    chunk_sec = st.slider("Chunk size (seconds)", 1.0, 6.0, 2.5, 0.5)

    # Session state for streaming ASR
    if "stream_asr" not in st.session_state:
        st.session_state["stream_asr"] = StreamingASRSession(chunk_seconds=chunk_sec)
    else:
        st.session_state["stream_asr"].chunk_seconds = chunk_sec

    sess: StreamingASRSession = st.session_state["stream_asr"]

    # WebRTC streamer
    from app.ui.pseudo_streaming import split_wav_to_chunks

st.markdown("### Fallback: Pseudo-Streaming (Guaranteed)")
st.write("If WebRTC streaming fails, use a saved WAV or upload a WAV and stream it in chunks.")

fallback_wav = st.file_uploader("Upload WAV for pseudo-streaming", type=["wav"], key="fallback_wav")

colF1, colF2 = st.columns(2)
with colF1:
    if st.button("Use last live WAV (if exists)", key="use_last_live_wav"):
        # reuse your existing live recording path if you saved one
        wav_path = st.session_state.get("live_wav_path")
        if wav_path and os.path.exists(wav_path):
            st.session_state["pseudo_wav_path"] = wav_path
            st.success(f"Using: {wav_path}")
        else:
            st.error("No live WAV found. Record and click 'Save Recording to WAV' first.")

with colF2:
    if fallback_wav:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix="_fallback.wav") as tmp:
            tmp.write(fallback_wav.read())
            st.session_state["pseudo_wav_path"] = tmp.name
        st.success("Fallback WAV uploaded.")

pseudo_chunk_sec = st.slider("Pseudo-stream chunk size (seconds)", 1.0, 8.0, 2.5, 0.5, key="pseudo_chunk_sec")

if st.button("Run Pseudo-Streaming ASR", key="run_pseudo_stream"):
    wav_path = st.session_state.get("pseudo_wav_path")
    if not wav_path or not os.path.exists(wav_path):
        st.error("Please provide a WAV file first.")
    else:
        st.audio(wav_path)
        chunks = split_wav_to_chunks(wav_path, chunk_seconds=pseudo_chunk_sec)

        full_text = ""
        prog = st.progress(0)
        out_box = st.empty()

        for i, ch in enumerate(chunks, start=1):
            asr_res = pipeline.asr_agent.transcribe(ch)  # adjust name if needed
            if asr_res.text:
                full_text = (full_text + " " + asr_res.text.strip()).strip()

            out_box.text_area("Pseudo-Streaming Transcript (accumulated)", full_text, height=220)
            prog.progress(int(i / len(chunks) * 100))

        st.success("Pseudo-streaming done.")
        st.session_state["pseudo_stream_text"] = full_text

    from streamlit_webrtc import webrtc_streamer, WebRtcMode

    ctx = webrtc_streamer(
    key="streaming_asr",
    mode=WebRtcMode.SENDONLY,
    rtc_configuration=RTC_CONFIG,
    media_stream_constraints={"audio": True, "video": False},
    audio_receiver_size=256,
    )


    transcript_box = st.empty()
    status_box = st.empty()

    if ctx.state.playing:
        time.sleep(0.2)
        st.rerun()

    if ctx.state.playing:
        status_box.info("Recording... partial transcription running.")

        # Pull audio frames from receiver in a loop-like pattern.
        # Streamlit reruns, so we do limited work each run.
        frames = []
        if ctx.audio_receiver:
            try:
                frames = ctx.audio_receiver.get_frames(timeout=0.1)
            except Exception:
                frames = []

        for fr in frames:
            sess.push_frame(fr)

        chunk_path = sess.pop_chunk_if_ready()
        if chunk_path:
            try:
                # Use your existing ASR agent via pipeline.asr_agent
                # (we reuse the same Whisper model & settings)
                asr_res = pipeline.asr_agent.transcribe(chunk_path)

                # Update texts
                sess.partial_text = asr_res.text.strip()
                if sess.partial_text:
                    sess.full_text = (sess.full_text + " " + sess.partial_text).strip()

                # Optional: show last chunk wav
                st.caption("Last audio chunk processed:")
                st.audio(chunk_path)

            except Exception as e:
                st.error(f"ASR chunk failed: {e}")

        transcript_box.text_area(
            "Live Transcript (accumulated)",
            value=sess.full_text,
            height=220
        )
    else:
        status_box.warning("Click Start in the WebRTC component to begin.")
        transcript_box.text_area(
            "Live Transcript (accumulated)",
            value=sess.full_text if "stream_asr" in st.session_state else "",
            height=220
        )

    colA, colB = st.columns(2)
    with colA:
        if st.button("Clear Transcript", key="clear_stream_asr"):
            st.session_state["stream_asr"] = StreamingASRSession(chunk_seconds=chunk_sec)
            st.success("Cleared.")
    with colB:
        if st.button("Run LLM on Current Transcript", key="llm_on_stream_text"):
            if not sess.full_text.strip():
                st.error("No transcript yet.")
            else:
                with st.spinner("Generating SOAP note from current transcript..."):
                    soap = pipeline.llm_agent.generate_soap(sess.full_text)
                st.subheader("SOAP Note (from live transcript)")
                st.write(soap)
