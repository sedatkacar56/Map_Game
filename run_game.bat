@echo off
echo Starting Map Strategy Game...
echo.

REM Check if virtual environment exists
if not exist "Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv Map_Game
)

REM Activate virtual environment
call Scripts\activate.bat

REM Install requirements if needed
pip install -r requirements.txt --quiet

REM Run the game
echo.
echo Opening game in browser...
streamlit run app.py

pause