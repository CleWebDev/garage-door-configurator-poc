@echo off
echo Setting up Garage Door Configurator...
echo.

REM Check if we're in the right directory
if not exist "app.py" (
    echo Error: app.py not found in current directory
    echo Please run this script from the garage-door-app root directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo Error: requirements.txt not found
    echo Please ensure all files are copied to the directory
    echo Current directory: %CD%
    dir /b *.txt
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    echo Please ensure Python 3.8+ is installed
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip and install build tools first
echo Upgrading pip and installing build tools...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo Error: Failed to upgrade pip and setuptools
    echo Check your Python installation
    pause
    exit /b 1
)

REM Install dependencies with prefer-binary flag to avoid building from source
echo Installing dependencies (using pre-built wheels when possible)...
pip install --prefer-binary -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    echo Trying individual package installation as fallback...
    pip install flask pandas numpy scikit-learn joblib aiohttp openai requests gunicorn
    if errorlevel 1 (
        echo Error: Package installation failed completely
        echo You may need to use Python 3.11 or 3.12 instead of 3.13
        pause
        exit /b 1
    )
)

REM Create empty __init__.py file
echo. > models\__init__.py

REM Run setup script
echo Running application setup...
python setup.py
if errorlevel 1 (
    echo Error: Setup script failed
    pause
    exit /b 1
)

echo.
echo ================================================================
echo Setup completed successfully!
echo ================================================================
echo.
echo Next steps:
echo 1. Add your garage door images to static\images\
echo 2. Set OPENAI_API_KEY environment variable
echo 3. Run: python app.py
echo.
echo Press any key to continue...
pause >nul