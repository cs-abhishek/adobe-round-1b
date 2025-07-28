@echo off
echo Adobe Hackathon 2025 - Document Intelligence System
echo ================================================

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

:: Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%

:: Install dependencies
echo.
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

:: Download NLTK data
echo.
echo Downloading NLTK data...
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)"

:: Try to download sentence transformer model
echo.
echo Downloading sentence transformer model...
python -c "try: from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2'); print('Model downloaded successfully'); except: print('Could not download sentence transformer model')"

:: Create directories
echo.
echo Creating directories...
if not exist "app\input" mkdir "app\input"
if not exist "app\output" mkdir "app\output"
if not exist "logs" mkdir "logs"

:: Run the system
echo.
echo Setup complete! Running document intelligence system...
echo.
python main.py

echo.
echo Processing complete. Check app\output\analysis.json for results.
pause
