@echo off
ECHO Starting Backend and Frontend Servers...

REM Activate the virtual environment and start the backend server in a new window
ECHO Starting Backend Server (Uvicorn)...
start "Backend Server" cmd /k ".\.venv\Scripts\activate && uvicorn app.main:app --reload"

REM Add a small delay to allow the backend to start up
timeout /t 3 /nobreak > NUL

REM Activate the virtual environment and start the frontend server in a new window
ECHO Starting Frontend UI (Streamlit)...
start "Frontend UI" cmd /k ".\.venv\Scripts\activate && streamlit run ui/app.py"

ECHO Both servers are starting in new windows.