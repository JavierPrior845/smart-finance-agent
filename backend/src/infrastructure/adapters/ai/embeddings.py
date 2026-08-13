from sentence_transformers import SentenceTransformer

class LocalEmbedder:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            # paraphrase-multilingual-MiniLM-L12-v2 yields 384 dimensions
            cls._model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        return cls._model

    @classmethod
    def get_embedding(cls, text: str) -> list[float]:
        if not text:
            return [0.0] * 384
        model = cls.get_model()
        embedding = model.encode(text)
        return embedding.tolist()
