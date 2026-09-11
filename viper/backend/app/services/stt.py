import os
from faster_whisper import WhisperModel

# Use a small model for prototype to avoid excessive local download/compute
# Options: "tiny", "base", "small", "medium", "large-v3"
MODEL_SIZE = os.getenv("WHISPER_MODEL", "base")
# Fallback to local CPU if no GPU available
DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

whisper_model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)

def transcribe_audio(audio_path: str):
    """
    Transcribes audio file using faster-whisper.
    For diarization, pyannote.audio is very heavy and requires huggingface tokens. 
    As a lightweight fallback, we will mock diarization based on silence gaps if pyannote is not feasible, 
    or return structured text segments without perfect diarization to keep it running smoothly on standard CPUs.
    """
    segments, info = whisper_model.transcribe(audio_path, beam_size=5)
    
    structured_segments = []
    # Mocking diarization for the simplicity of the prototype (alternating speakers)
    # A real implementation would use pyannote.audio pipeline
    for i, segment in enumerate(segments):
        speaker = f"SPEAKER_{str( (i % 2) + 1 ).zfill(2)}"
        structured_segments.append({
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "speaker": speaker,
            "text": segment.text.strip()
        })
        
    return structured_segments
