from config.envs import VDB_DIR, MONGO_URI, MONGO_DB
from pymongo import MongoClient
from modules.retrieve import RemoteEmbedding
from langchain_chroma import Chroma

def load_extracted(collection_name: str = "chunks") -> list:
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    chunks_col = db[collection_name]

    docs = []
    for meta in chunks_col.find({}):
        docs.append({
            "file": meta["file"],
            "text": meta["text"],
            "chunk_id": f"{meta['file']}_{meta['section']}"
        })
    return docs

def ingest_chunks(collection_name: str = "chunks") -> None:
    docs = load_extracted()
    embed_model = RemoteEmbedding()
    db = Chroma(
        persist_directory=VDB_DIR,
        embedding_function=embed_model,
        collection_name=collection_name
    )

    files = set(d["file"] for d in docs)
    for pdf_file in files:
        all_docs = db._collection.get()
        old_ids = [
            id_ for id_, meta in zip(all_docs["ids"], all_docs["metadatas"])
            if meta.get("file") == pdf_file
        ]
        
        if old_ids:
            db._collection.delete(ids=old_ids)

        file_docs = [d for d in docs if d["file"] == pdf_file]
        texts = [d["text"] for d in file_docs]
        metadatas = [{"file": d["file"], "chunk_id": d["chunk_id"]} for d in file_docs]
        db.add_texts(texts=texts, metadatas=metadatas)
