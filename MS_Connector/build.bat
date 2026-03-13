@echo off
REM ============================================
REM MS FEZForge - Build Windows Executable
REM ============================================
REM
REM This script builds a standalone .exe file
REM that can be run on any Windows computer
REM without needing Python installed.
REM
REM Prerequisites:
REM   pip install -r requirements.txt
REM
REM Output:
REM   dist\MS_FEZForge.exe
REM ============================================

echo.
echo ============================================
echo  Building MS FEZForge Executable
echo ============================================
echo.

REM Check if pyinstaller is installed
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: PyInstaller not found.
    echo Please install it: pip install pyinstaller
    echo.
    pause
    exit /b 1
)

REM Build using spec file
echo Building with PyInstaller...
echo.
pyinstaller ms_fezforge.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: Build failed. Check the output above for details.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Build Successful!
echo ============================================
echo.
echo Executable: dist\MS_FEZForge.exe
echo.
echo To use:
echo   1. Copy dist\MS_FEZForge.exe to your desired location
echo   2. Make sure config.json is in the same folder as the exe
echo   3. Double-click MS_FEZForge.exe to run
echo.
pause
