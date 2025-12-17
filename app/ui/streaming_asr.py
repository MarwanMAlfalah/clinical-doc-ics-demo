import os
import time
import wave
import tempfile
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np
import av


def _frame_to_pcm16_mono(frame: av.AudioFrame) -> np.ndarray:
    """
    Convert an incoming AudioFrame to mono int16 PCM.
    Handles common cases from browser mic.
    """
    pcm = frame.to_ndarray()  # shape: (channels, samples) or (samples,)
    if pcm.ndim == 2:
        # average channels -> mono
        pcm = pcm.mean(axis=0)

    # Ensure int16
    if pcm.dtype != np.int16:
        # Many browsers provide float32 in [-1, 1]
        pcm = np.clip(pcm, -1.0, 1.0)
        pcm = (pcm * 32767.0).astype(np.int16)

    return pcm


def _write_wav(path: str, pcm16: np.ndarray, sample_rate: int) -> None:
    """
    Write mono int16 PCM into WAV file.
    """
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # int16
        wf.setframerate(sample_rate)
        wf.writeframes(pcm16.tobytes())


@dataclass
class StreamingASRSession:
    """
    Collects audio frames, cuts into chunks, and produces partial transcripts.
    """
    sample_rate: int = 48000
    chunk_seconds: float = 2.5
    buffer_pcm: List[np.ndarray] = field(default_factory=list)
    last_chunk_time: float = field(default_factory=time.time)
    partial_text: str = ""
    full_text: str = ""
    last_chunk_wav: Optional[str] = None

    def push_frame(self, frame: av.AudioFrame):
        pcm = _frame_to_pcm16_mono(frame)
        self.buffer_pcm.append(pcm)

    def _buffer_duration_seconds(self) -> float:
        if not self.buffer_pcm:
            return 0.0
        total_samples = int(sum(x.shape[0] for x in self.buffer_pcm))
        return total_samples / float(self.sample_rate)

    def pop_chunk_if_ready(self) -> Optional[str]:
        """
        If buffer duration >= chunk_seconds, write a WAV chunk and clear buffer.
        Returns path to chunk WAV or None.
        """
        if self._buffer_duration_seconds() < self.chunk_seconds:
            return None

        pcm16 = np.concatenate(self.buffer_pcm, axis=0)
        self.buffer_pcm.clear()

        tmp_dir = tempfile.gettempdir()
        chunk_path = os.path.join(tmp_dir, f"asr_chunk_{int(time.time()*1000)}.wav")
        _write_wav(chunk_path, pcm16, self.sample_rate)

        self.last_chunk_wav = chunk_path
        return chunk_path
