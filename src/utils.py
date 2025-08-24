import os
from config import DOCS_DIR, VDB_DIR, MONGO_URI, MONGO_DB
from langchain_chroma import Chroma
from pymongo import MongoClient
from retrieve import RemoteEmbedding

PERSIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", VDB_DIR))

def remove_deleted_mongodb_chunks():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]

    existing_files = {
        f for f in os.listdir(DOCS_DIR)
        if f.lower().endswith(".pdf")
    }

    for collection_name in db.list_collection_names():
        col = db[collection_name]
        all_files_in_db = {doc["file"] for doc in col.find({}, {"file": 1}) if "file" in doc}

        deleted_files = all_files_in_db - existing_files
        if deleted_files:
            col.delete_many({"file": {"$in": list(deleted_files)}})

def remove_deleted_chromadb_chunks(collection_name: str = "chunks"):
    embed_model = RemoteEmbedding()
    db = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embed_model,
        collection_name=collection_name,
    )

    existing_files = set(
        f for f in os.listdir(DOCS_DIR) if f.lower().endswith(".pdf")
    )

    all_vectors = db._collection.get()
    metadatas = all_vectors["metadatas"]

    deleted_ids = [meta["chunk_id"] for meta in metadatas if meta.get("file") not in existing_files]
    if deleted_ids:
        db._collection.delete(ids=deleted_ids)

def clean_dbs():
    remove_deleted_mongodb_chunks()
    remove_deleted_chromadb_chunks()
