# CVision

AI-Powered CV Recommendation System with Retrieval-Augmented Generation and Automated Ranking

---

## Table of Contents

- [Project Overview](#project-overview)
- [Installation](#installation)
  - [Local Installation](#local-installation)
  - [Docker Installation](#docker-installation)
- [Technologies Used](#technologies-used)
- [Execution](#execution)
  - [Local Execution](#local-execution)
  - [Docker Execution](#docker-execution)
- [License](#license)

---

## Project Overview

### Concept

CVision is an ICL system designed to streamline CV evaluation and candidate recommendation through **Retrieval-Augmented Generation (RAG)**. Instead of manually reviewing CVs, the system processes them in batches using an LLM to extract structured chunks such as Experience, Projects, Skills, Certifications, and Education, preserving every critical detail. These chunks are stored in a **Vector Store**, allowing CVision to dynamically reconstruct candidate profiles by retrieving the most relevant chunks for a given job description. Finally, a scoring module ranks candidates based on a weighted evaluation of their qualifications, providing transparent and detailed explanations for each score.

### Challenges

Developing CVision involved several technical and operational challenges:

- **Comprehensive information extraction:** Capturing all relevant details from diverse CV formats without losing context.  
- **Efficient retrieval:** Querying large CV datasets quickly to identify the most relevant candidate information.  
- **Dynamic candidate profiling:** Assembling only the top relevant chunks to generate a query-specific CV view for evaluation.  
- **Objective scoring:** Creating a scoring system that fairly weighs experience, projects, skills, certifications and education.  

### Solution

CVision addresses these challenges with a combination of AI and database design:

- **LLM-based chunk extraction:** Converts CVs into structured JSON chunks that maintain full details for accurate downstream processing.  
- **ChromaDB storage and retrieval:** Enables fast, relevance-based access to CV chunks for job-specific queries.  
- **Dynamic reconstruction:** Reassembles only the most relevant chunks to produce tailored candidate profiles using **Semantic Search Similarity**.  
- **Weighted scoring with LLM explanations:** Provides scores from 0–100 along with rationale, making recommendations transparent and interpretable.  

This approach allows recruiters to quickly identify the best candidates while maintaining a high level of accuracy and explainability.  

---

## Installation

### Local Installation

1. Clone this repository or download the `.zip` archive and extract it.  
2. Create a `.env` file in the project root containing all required environment variables.  
3. Open a terminal in the project folder.  
4. Run `make env` to create a virtual environment and install all dependencies.  

### Docker Installation

1. Clone this repository or download the `.zip` archive and extract it.  
2. Ensure **Docker** and **Docker Compose** are installed.  
3. Create a `.env` file in the project root with the required environment variables.  
4. Open a terminal in the project folder.  
5. Run `docker-compose build` to build the container.  

---

## Technologies Used

- Python  
- GPT-OSS (Hugging Face API Inference)  
- PyMuPDF  
- LangChain & ChromaDB  
- Streamlit (GUI)  
- Docker & Docker Compose  

Both local and Docker approaches use the same codebase and dependencies.

---

## Execution

### Local Execution

1. Start the application by running `make start`.  
2. Open your browser and go to <http://localhost:8501>.  
3. Stop the application by running `make stop`.  

> Notes:  
>
> - Compatible with Windows, Linux, and macOS.  
> - The local setup directly runs the application on the host machine.  

### Docker Execution

1. Ensure **Docker Desktop** is running.  
2. Start the containers by running `docker-compose up`.  
3. Open your browser and go to <http://localhost:8501>.  
4. Stop the containers by running `docker-compose down`.  

> Notes:  
>
> - Docker provides a consistent environment across all platforms.  
> - Environment variables in `.env` must be correctly set before building and running containers.  

---

## License

This project is licensed under the **Apache License**, see the `LICENSE` file for details.
