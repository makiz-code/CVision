from utils import clean_dbs
from extract import extract_chunks
from ingest import ingest_chunks
from retrieve import retrieve_chunks
from ranker import rank_candidates

def match_cvs(role: str):
    try:
        clean_dbs()

        yield "Extracting Chunks..."
        extract_chunks()
        yield "Chunks Extracted ✅"

        yield "Ingesting Chunks..."
        ingest_chunks()
        yield "Chunks Ingested ✅"

        yield "Retrieving Chunks..."
        chunks = retrieve_chunks(role)
        yield "Chunks Retrieved ✅"

        yield "Ranking Candidates..."
        ranked = rank_candidates(role, chunks)
        yield "Candidates Ranked ✅"

        yield {"results": ranked}
    except Exception as e:
        yield f"Error in match_cvs: {e}"
