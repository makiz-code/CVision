.PHONY: env start stop

# --- Build Env ---
env:
ifeq ($(OS),Windows_NT)
	python -m venv app\.venv
	app\.venv\Scripts\python.exe -m pip install --upgrade pip
	app\.venv\Scripts\python.exe -m pip install --no-cache-dir -r app\requirements.txt
else
	python3 -m venv app/.venv
	app/.venv/bin/python -m pip install --upgrade pip
	app/.venv/bin/python -m pip install --no-cache-dir -r app/requirements.txt
endif

# --- Run App ---
start:
ifeq ($(OS),Windows_NT)
	cmd.exe /C start "" powershell -NoExit -Command "$$host.UI.RawUI.WindowTitle = 'PROGRAM'; app\.venv\Scripts\python.exe -m streamlit run app\src\app.py"
else
	gnome-terminal -- bash -c "app/.venv/bin/python -m streamlit run app/src/app.py; exec bash" || \
	osascript -e 'tell app "Terminal" to do script \"app/.venv/bin/python -m streamlit run app/src/app.py\"'
endif

# --- Stop App ---
stop:
ifeq ($(OS),Windows_NT)
	-@taskkill /F /IM python.exe >nul 2>&1
	-@taskkill /FI "WINDOWTITLE eq PROGRAM*"
else
	-pkill -f "python -m streamlit run app/src/app.py"
endif
