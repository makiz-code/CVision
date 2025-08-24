import json
import re
from config import MONGO_URI, MONGO_DB, LLM_BATCH_SIZE, TOP_K_CVS
from pymongo import MongoClient
from prompt import query_llm

def load_candidate_sections(src_file: str, collection_name: str = "chunks") -> dict:
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    chunks_col = db[collection_name]

    candidate_sections = {}
    for data in chunks_col.find({"file": src_file}):
        candidate_sections[data["section"]] = data["text"]
    return candidate_sections

def build_ranking_prompt(role: str, candidates: dict) -> str:
    prompt = (
        "You are a highly experienced recruiter and evaluator. "
        "Assess the candidates for the following role carefully and objectively:\n\n"
    )
    prompt += f"Role Description:\n{role}\n\n"

    prompt += "Candidate profiles with structured sections:\n\n"
    for i, (src, sections) in enumerate(candidates.items(), 1):
        prompt += f"Source File: {src}\n"
        for name, text in sections.items():
            prompt += f"{name.upper()}:\n{text}\n"
        prompt += "\n"

    prompt += '''
        Instructions:
        - Evaluate each candidate's overall suitability based on the relevance and quality of their content.
        - Use a weighted evaluation approach:
            * Practical EXPERIENCE & PROJECTS relevant to the role: 50%
            * Relevant SKILLS: 30%
            * EDUCATION: 10%
            * CERTIFICATIONS: 10%
        - Focus on measurable contributions, outcomes, tools, technologies, and responsibilities in experience and projects.
        - Do NOT inflate scores for general or unrelated academic background, degrees, or certifications.
        - Assign a score from 0 to 100 (integer) reflecting overall suitability.
        - Provide a concise, objective explanation (4-5 sentences) justifying the score with specific references to sections.
        - If a section is missing, treat it as empty but do not penalize excessively.
        - Always refer to each candidate by their FULL NAME as extracted from their CV or profile.
        - Do NOT use gendered pronouns (e.g., he, she, him, her); remain neutral in all references.
        - Respond ONLY in valid JSON format exactly as below:
        [
            {"file": "<filename>", "score": <int>, "explanation": "<text>"}
        ]
        - Ensure the JSON is fully parsable, with double quotes and no extra text outside the array.
        - For tie-breaking, prioritize depth, relevance, and recency of experience and projects over general skills or education.
        - Keep evaluations consistent, objective, and clearly tied to evidence in the candidate's profile.
    '''

    return prompt

def rank_candidates(role: str, chunks: list):
    candidates = {}
    for d in chunks:
        src = d.metadata.get("file", "unknown")
        candidates.setdefault(src, []).append(d.page_content)

    candidates_sections = {}
    for src in candidates.keys():
        sections = load_candidate_sections(src)
        if sections:
            candidates_sections[src] = sections

    results = []
    candidate_keys = list(candidates_sections.keys())
    
    for i in range(0, len(candidate_keys), LLM_BATCH_SIZE):
        batch_keys = candidate_keys[i:i+LLM_BATCH_SIZE]
        batch_candidates = {k: candidates_sections[k] for k in batch_keys}
        prompt = build_ranking_prompt(role, batch_candidates)
        try:
            output = query_llm(prompt)
        except Exception:
            output = "[]"
        try:
            match = re.search(r'\[.*\]', output, re.DOTALL)
            batch_results = json.loads(match.group(0)) if match else []
        except Exception:
            batch_results = []

        for r in batch_results:
            results.append(r)

    results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)[:TOP_K_CVS]

    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    col = db["rankings"]
    for r in results:
        col.update_one(
            {"file": r["file"], "job_hash": hash(role)},
            {"$set": {
                "score": r.get("score", 0),
                "explanation": r.get("explanation", ""),
                "job": role
            }},
            upsert=True
        )

    return results
