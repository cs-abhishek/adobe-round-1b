@echo off
title Adobe Hackathon 2025 - Document Intelligence System
color 0A

echo.
echo 🏆 ===============================================================
echo    ADOBE HACKATHON 2025 - ROUND 1B
echo    Persona-Driven Document Intelligence System
echo ===============================================================
echo.

:: Check if Python is installed
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo 📥 Please install Python 3.8 or higher from https://python.org
    echo.
    pause
    exit /b 1
)

:: Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Found Python %PYTHON_VERSION%

:: Create necessary directories
echo.
echo 📁 Creating project directories...
if not exist "app\input" mkdir "app\input"
if not exist "app\output" mkdir "app\output"
if not exist "logs" mkdir "logs"
if not exist "models" mkdir "models"
echo ✅ Directories created

:: Install dependencies
echo.
echo 📦 Installing dependencies...
echo    This may take a few minutes for first-time setup...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo ❌ Failed to install some dependencies
    echo 🔄 Trying with fallback installation...
    python -m pip install PyPDF2 scikit-learn numpy nltk --quiet
)

:: Download NLTK data
echo.
echo 🧠 Downloading NLTK language data...
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); print('✅ NLTK data ready')"

:: Try to download sentence transformer model
echo.
echo 🤖 Checking AI models...
python -c "try: from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2'); print('✅ Sentence transformer model ready'); except: print('⚠️  Sentence transformer not available, using TF-IDF fallback')"

:: Check for input files
echo.
echo 📄 Checking for input documents...
if exist "app\input\*.pdf" (
    echo ✅ Found PDF files in app\input\
) else if exist "app\input\*.txt" (
    echo ✅ Found text files in app\input\
) else (
    echo ⚠️  No PDF or text files found in app\input\
    echo 📥 Creating demo documents...
    python create_demo.py
)

:: Check persona configuration
echo.
echo 👤 Checking persona configuration...
if exist "app\persona.json" (
    echo ✅ Persona configuration found
) else (
    echo 📝 Creating default persona configuration...
    echo {"persona": "Data scientist working in healthcare research", "job": "Find machine learning techniques for medical image analysis"} > app\persona.json
)

:: Run the system
echo.
echo 🚀 ===============================================================
echo    STARTING DOCUMENT INTELLIGENCE ANALYSIS
echo ===============================================================
echo.

:: Run with time measurement
echo ⏱️  Starting analysis at %TIME%...
set START_TIME=%TIME%

python main.py

set END_TIME=%TIME%
echo.
echo ⏱️  Analysis completed at %END_TIME%

:: Check results
echo.
echo 📊 ===============================================================
echo    ANALYSIS RESULTS
echo ===============================================================

if exist "app\output\analysis.json" (
    echo ✅ Analysis completed successfully!
    echo 📄 Results saved to: app\output\analysis.json
    
    :: Display file size
    for %%F in ("app\output\analysis.json") do (
        echo 📏 Output file size: %%~zF bytes
    )
    
    :: Quick stats from the output
    python -c "
import json
try:
    with open('app/output/analysis.json', 'r') as f:
        data = json.load(f)
    print('📊 Quick Statistics:')
    print(f'   📚 Documents processed: {len(data[\"metadata\"][\"documents\"])}')
    print(f'   📑 Sections found: {len(data[\"extracted_sections\"])}')
    print(f'   📝 Subsections analyzed: {len(data[\"subsection_analysis\"])}')
    if 'performance' in data['metadata']:
        perf = data['metadata']['performance']
        print(f'   ⏱️  Processing time: {perf[\"processing_time\"]:.2f} seconds')
        print(f'   💾 Memory used: {perf[\"memory_delta_mb\"]:.1f} MB')
        if perf['processing_time'] <= 60:
            print('   ✅ Speed requirement met (≤60s)')
        else:
            print('   ⚠️  Speed requirement exceeded')
except Exception as e:
    print(f'Could not read results: {e}')
"
) else (
    echo ❌ Analysis failed - no output file generated
    echo 📋 Check the console output above for error details
)

:: Offer additional options
echo.
echo 🔧 ===============================================================
echo    ADDITIONAL OPTIONS
echo ===============================================================
echo.
echo Available commands:
echo   1. python benchmark.py    - Run performance benchmarks
echo   2. python test_system.py  - Run system tests
echo   3. python create_demo.py  - Create demo documents
echo.

:: Final status
if exist "app\output\analysis.json" (
    echo 🎉 HACKATHON SUBMISSION READY! 🎉
    echo 📁 Check app\output\ for your results
) else (
    echo ⚠️  Please check for errors and try again
)

echo.
echo Press any key to exit...
pause >nul
