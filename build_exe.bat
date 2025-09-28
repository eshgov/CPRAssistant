@echo off
echo Building Improved CPR Assistant Executable
echo ==========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo Error: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Install requirements
echo Installing requirements...
pip install -r improved_requirements.txt
if errorlevel 1 (
    echo Error: Failed to install requirements
    pause
    exit /b 1
)

REM Clean previous build
echo Cleaning previous build...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build the executable
echo Building executable...
pyinstaller improved_cpr_assistant.spec
if errorlevel 1 (
    echo Error: Failed to build executable
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo Executable location: dist\ImprovedCPRAssistant.exe
echo.
echo You can now run the executable by double-clicking it or running:
echo dist\ImprovedCPRAssistant.exe
echo.
pause
