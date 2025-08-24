import os
from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
EMBED_MODEL = os.getenv("EMBED_MODEL")
LLM_MODEL = os.getenv("LLM_MODEL")

VDB_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")

VEC_BATCH_SIZE=64
LLM_BATCH_SIZE=4
TOP_K_CHUNKS=100
TOP_K_CVS=10
