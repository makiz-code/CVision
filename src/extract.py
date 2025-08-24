import os
import fitz
import re
import json
from config import DOCS_DIR, LLM_BATCH_SIZE, MONGO_URI, MONGO_DB
from tqdm import tqdm
from prompt import query_llm
from pymongo import MongoClient

def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_text_from_pdf(pdf_path: str) -> str:
    full_text: list[str] = []
    doc = fitz.open(pdf_path)
    for page in doc:
        page_text = clean_text(page.get_text("text"))
        if page_text:
            full_text.append(page_text)
    doc.close()
    return "\n".join(full_text)

def build_extraction_prompt(texts_with_filenames: list[tuple[str, str]]) -> str:
    prompt = "You are an expert recruiter and data extractor. Extract all meaningful information from CVs accurately and completely.\n\n"

    for i, (text, pdf_file) in enumerate(texts_with_filenames, 1):
        prompt += f"CV {i} (filename: {pdf_file}):\n{text}\n\n"

    prompt += '''
        Instructions:
        - Extract all relevant information from each CV; do NOT summarize or omit any meaningful details.
        - Organize content into sections if present: Experience, Education, Skills, Certifications, Projects.
        - Within each section, separate individual items with line breaks, so that each project, degree, certification, or experience entry is clearly distinct.
        - Preserve the full text of each section, including roles, responsibilities, projects, dates, tools, technologies, and accomplishments.
        - Remove only repeated headers, page numbers, formatting artifacts, or irrelevant symbols.
        - If a section is missing, leave it as an empty string.
        - Maintain clarity, proper sentence structure, and readability.
        - Respond ONLY in valid JSON format exactly as below:
        [
            {"Experience": "...", "Education": "...", "Skills": "...", "Certifications": "...", "Projects": "...", "file": "..."}
        ]
        - Ensure the JSON is fully parsable with double quotes and no extra text outside the array.
        - Keep content consistent across CVs for reliable automated scoring.
        - Prioritize preserving information that demonstrates skills, achievements, responsibilities, and measurable outcomes.
        - Do not condense or abstract content; every detail may be relevant for downstream ranking.
        - Ensure the output is structured, clean, and machine-readable.
    '''
    
    return prompt

def segment_cvs_with_llm(texts_with_filenames, max_retries: int = 2) -> list[dict[str, str]]:
    if not texts_with_filenames:
        return [{} for _ in texts_with_filenames]
    
    prompt = build_extraction_prompt(texts_with_filenames)
    for attempt in range(max_retries + 1):
        try:
            structured_text = query_llm(prompt)
            if not structured_text.strip():
                continue
            match = re.search(r'\[.*\]', structured_text, re.DOTALL)
            if not match:
                prompt += "\n\nThe previous output was invalid JSON. Please provide ONLY valid JSON in the requested format."
                continue
            json_text = match.group(0).replace("’", "'").replace("“", '"').replace("”", '"')
            data = json.loads(json_text)
            if not isinstance(data, list):
                prompt += "\n\nThe previous output was not a list. Please provide a list of CV sections in the correct format."
                continue
            for cv, (_, pdf_file) in zip(data, texts_with_filenames):
                cv["file"] = pdf_file
                for section in ["Experience", "Education", "Skills", "Certifications", "Projects"]:
                    if section not in cv:
                        cv[section] = ""
            return data
        
        except json.JSONDecodeError:
            prompt += "\n\nThe previous output could not be parsed as JSON. Please provide valid JSON as instructed."
            continue
        except Exception as e:
            prompt += f"\n\nAn error occurred: {str(e)}. Please provide valid JSON output."
            continue

    return [{} for _ in texts_with_filenames]

def extract_chunks(collection_name: str = "chunks"):
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    chunks_col = db[collection_name]

    pdf_files = sorted([f for f in os.listdir(DOCS_DIR) if f.lower().endswith(".pdf")])
    all_texts_with_filenames = [(extract_text_from_pdf(os.path.join(DOCS_DIR, f)), f) for f in pdf_files]

    for i in tqdm(range(0, len(all_texts_with_filenames), LLM_BATCH_SIZE), desc="Extraction CVs"):
        batch = all_texts_with_filenames[i:i+LLM_BATCH_SIZE]
        structured_sections_list = segment_cvs_with_llm(batch)

        for (_, pdf_file), structured_sections in zip(batch, structured_sections_list):
            for section_name, section_text in structured_sections.items():
                if section_name == "file":
                    continue
                meta = {
                    "file": pdf_file,
                    "section": section_name,
                    "text": section_text.strip()
                }
                chunks_col.update_one(
                    {"file": pdf_file, "section": section_name},
                    {"$set": meta},
                    upsert=True
                )
