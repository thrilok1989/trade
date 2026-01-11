@echo off
REM Dhan Options Platform - Quick Setup Script for Windows

echo ==================================
echo Dhan Options Trading Platform
echo Quick Setup Script for Windows
echo ==================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo √ %PYTHON_VERSION% found
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo √ Virtual environment already exists
) else (
    python -m venv venv
    echo √ Virtual environment created
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo √ Virtual environment activated
echo.

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo √ Dependencies installed
echo.

REM Create .streamlit directory
echo Setting up Streamlit configuration...
if not exist .streamlit (
    mkdir .streamlit
    echo √ Created .streamlit directory
)

REM Copy secrets template
if not exist .streamlit\secrets.toml (
    if exist .streamlit\secrets.toml.template (
        copy .streamlit\secrets.toml.template .streamlit\secrets.toml
        echo √ Created secrets.toml from template
        echo   -^> Edit .streamlit\secrets.toml with your credentials
    )
)
echo.

REM Display next steps
echo ==================================
echo Setup Complete! 🎉
echo ==================================
echo.
echo Next steps:
echo.
echo 1. Get your Dhan API credentials:
echo    - Login to https://dhan.co
echo    - Go to Settings -^> API
echo    - Generate Access Token
echo.
echo 2. Run the application:
echo    streamlit run dhan_options_platform_live.py
echo.
echo 3. Open your browser:
echo    http://localhost:8501
echo.
echo 4. Enter your credentials in the sidebar
echo.
echo ==================================
echo Happy Trading! 📈📊
echo ==================================
echo.
pause
