"""
Utilidad de embeddings locales usando sentence-transformers.
Modelo: all-MiniLM-L6-v2 (384 dimensiones, ~90MB, corre en CPU)
Se descarga automaticamente de HuggingFace en el primer uso.
"""

_model = None
MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


def get_embedding(text: str) -> list[float]:
    """Genera un embedding para el texto dado. Carga el modelo en el primer llamado."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        print(f"[Embeddings] Cargando modelo {MODEL_NAME}...")
        _model = SentenceTransformer(MODEL_NAME)
        print("[Embeddings] Modelo listo.")
    return _model.encode(text, normalize_embeddings=True).tolist()
