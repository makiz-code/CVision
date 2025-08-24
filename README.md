# CVision

CVision is an intelligent CV recommendation system that uses Retrieval-Augmented Generation (RAG) to optimize the selection and automatic ranking of the most relevant profiles based on a given job description.

## Prerequisites

Before starting, ensure you have the following installed:

- **Docker**  
- **Docker Compose**  

## Installation

1. **Download the project:**  
   Clone this repository or download the `.zip` archive and extract it.

2. **Configure environment variables:**  
   Create a .env file in the project folder containing all variables required by docker-compose.yml, ensuring the keys and values match the backend service configuration.

## Running the project

Make sure Docker Desktop is running before launching anything  
Run the following command to create the containers: docker-compose build  
Run the following command to launch the containers: docker-compose up -d  
Open your web browser and go to <http://localhost:8501> to access the app  
Run the following command to shut down the containers: docker-compose down
