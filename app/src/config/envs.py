import os
from dotenv import load_dotenv

if not os.environ.get("MONGO_DB"):
    load_dotenv()

MONGO_DB = os.getenv("MONGO_DB")
MONGO_URI = os.getenv("MONGO_URI")

HF_API_TOKEN = os.getenv("HF_API_TOKEN")

VEC_MODEL = os.getenv("VEC_MODEL")
LLM_MODEL = os.getenv("LLM_MODEL")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

VDB_DIR = os.path.join(BASE_DIR, "data")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

VEC_BATCH_SIZE=64
LLM_BATCH_SIZE=4
TOP_K_CHUNKS=100
TOP_K_CVS=10
