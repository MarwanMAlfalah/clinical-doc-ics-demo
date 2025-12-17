import os
import math
import wave
import tempfile
from typing import List

def split_wav_to_chunks(wav_path: str, chunk_seconds: float = 2.5) -> List[str]:
    """
    Splits a mono/stereo WAV into smaller WAV chunk files.
    Returns list of chunk file paths in order.
    """
    out_paths = []
    with wave.open(wav_path, "rb") as wf:
        nch = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        fr = wf.getframerate()
        nframes = wf.getnframes()

        frames_per_chunk = int(fr * chunk_seconds)
        total_chunks = int(math.ceil(nframes / frames_per_chunk))

        for i in range(total_chunks):
            wf.setpos(i * frames_per_chunk)
            frames = wf.readframes(frames_per_chunk)

            if not frames:
                break

            out = os.path.join(
                tempfile.gettempdir(),
                f"wav_chunk_{i}_{int(chunk_seconds*1000)}ms_{os.path.basename(wav_path)}"
            )

            with wave.open(out, "wb") as wout:
                wout.setnchannels(nch)
                wout.setsampwidth(sampwidth)
                wout.setframerate(fr)
                wout.writeframes(frames)

            out_paths.append(out)

    return out_paths
