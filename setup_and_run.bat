@echo off
REM Create virtual environment only if it doesn't exist
if not exist venv (
    echo [*] Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo [*] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Run the bot script
echo [*] Running bot...
python instagram_bot.py

REM Keep console open after running
pause
