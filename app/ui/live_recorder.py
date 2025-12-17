import queue
import numpy as np
import soundfile as sf

_audio_q = queue.Queue()

def push_audio_frame(audio_frame) -> None:
    """
    Called for every audio frame coming from browser mic.
    audio_frame: av.AudioFrame
    """
    # Convert to numpy float32
    pcm = audio_frame.to_ndarray()
    # pcm shape can be (channels, samples)
    if pcm.ndim == 2:
        pcm = pcm.T  # -> (samples, channels)
    _audio_q.put(pcm.astype(np.float32))

def drain_audio_to_wav(path: str, sample_rate: int = 48000) -> int:
    """
    Save all queued frames into a WAV file.
    Returns number of samples written.
    """
    chunks = []
    total = 0
    while True:
        try:
            x = _audio_q.get_nowait()
            chunks.append(x)
            total += x.shape[0]
        except queue.Empty:
            break

    if not chunks:
        return 0

    audio = np.concatenate(chunks, axis=0)
    sf.write(path, audio, sample_rate)
    return total
