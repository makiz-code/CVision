# CVision

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass  
.venv\Scripts\Activate.ps1
streamlit run .\src\app.py

docker-compose build
docker-compose up -d
start process <http://localhost:8501>
docker-compose down
