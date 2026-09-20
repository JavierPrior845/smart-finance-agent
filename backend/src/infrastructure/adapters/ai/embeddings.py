import logging
from sentence_transformers import SentenceTransformer
from src.config import settings

logger = logging.getLogger(__name__)

class LocalEmbedder:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            logger.info("Initializing embedding model (%s)...", settings.EMBEDDING_MODEL)
            # paraphrase-multilingual-MiniLM-L12-v2 yields 384 dimensions
            cls._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("Embedding model loaded successfully.")
        return cls._model

    @classmethod
    def warmup(cls):
        try:
            model = cls.get_model()
            model.encode("warmup")
            logger.info("Embedding model warmup completed.")
        except Exception as e:
            logger.warning("Warmup of embedding model failed: %s", e)

    @classmethod
    def get_embedding(cls, text: str) -> list[float]:
        if not text:
            return [0.0] * 384
        model = cls.get_model()
        embedding = model.encode(text)
        return embedding.tolist()
