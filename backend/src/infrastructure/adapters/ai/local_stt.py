import logging
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

# Initialize model globally so it stays in memory across tasks
_model = None

def get_whisper_model():
    global _model
    if _model is None:
        logger.info("Cargando modelo Whisper 'base' en CPU...")
        _model = WhisperModel("base", device="cpu", compute_type="int8")
        logger.info("Modelo Whisper cargado exitosamente.")
    return _model

def transcribe_audio(file_path: str) -> str:
    """
    Transcribes the given audio file using faster-whisper.
    Returns the concatenated text.
    """
    model = get_whisper_model()
    segments, info = model.transcribe(file_path, beam_size=5, language="es")
    
    text_chunks = []
    for segment in segments:
        text_chunks.append(segment.text)
        
    return " ".join(text_chunks).strip()
