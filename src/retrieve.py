import os
from config import VDB_DIR, EMBED_MODEL, HF_API_TOKEN, VEC_BATCH_SIZE, TOP_K_CHUNKS
from langchain_chroma import Chroma
from huggingface_hub import InferenceClient

PERSIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", VDB_DIR))

class RemoteEmbedding:
    def __init__(self, model_name=EMBED_MODEL, token=HF_API_TOKEN):
        self.client: InferenceClient = InferenceClient(model=model_name, token=token)
        self.model_name: str = model_name

    def embed_documents(self, texts: list) -> list:
        embeddings: list = []
        for i in range(0, len(texts), VEC_BATCH_SIZE):
            batch = texts[i:i+VEC_BATCH_SIZE]
            resp = self.client.feature_extraction(batch)
            embeddings.extend(resp)
        return embeddings

    def embed_query(self, text: str) -> list:
        return self.client.feature_extraction(text)

def retrieve_chunks(role: str, collection_name: str = "chunks") -> list:
    embed_model = RemoteEmbedding()
    db = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embed_model,
        collection_name=collection_name
    )

    retriever = db.as_retriever(search_kwargs={"k": TOP_K_CHUNKS})
    chunks = retriever.invoke(role)
    return chunks
