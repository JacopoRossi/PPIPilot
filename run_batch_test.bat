@echo off
REM ============================================================================
REM PPIPilot - Batch Execution Test Script
REM ============================================================================
REM This script demonstrates how to run batch analysis from command line
REM
REM Usage:
REM   1. Copy config_batch_template.json to config_batch.json
REM   2. Edit config_batch.json with your settings
REM   3. Run this script: run_batch_test.bat
REM ============================================================================

echo.
echo ================================================================================
echo PPIPilot - Batch Execution CLI
echo ================================================================================
echo.

REM Check if config file exists
if not exist "config_batch.json" (
    echo [ERROR] Configuration file not found: config_batch.json
    echo.
    echo Please create config_batch.json from the template:
    echo   copy config_batch_template.json config_batch.json
    echo.
    echo Then edit config_batch.json with your settings.
    echo.
    pause
    exit /b 1
)

echo [INFO] Configuration file found: config_batch.json
echo.

REM Display configuration (first 15 lines)
echo [INFO] Configuration preview:
echo --------------------------------------------------------------------------------
type config_batch.json | more /E /C /P
echo --------------------------------------------------------------------------------
echo.

REM Ask for confirmation
set /p confirm="Do you want to proceed with this configuration? (y/n): "
if /i not "%confirm%"=="y" (
    echo.
    echo [INFO] Execution cancelled by user.
    pause
    exit /b 0
)

echo.
echo [INFO] Starting batch execution...
echo.

REM Run the batch analysis
python interface_batch_cli.py config_batch.json

REM Check exit code
if %errorlevel% equ 0 (
    echo.
    echo ================================================================================
    echo [SUCCESS] Batch execution completed successfully!
    echo ================================================================================
    echo.
) else (
    echo.
    echo ================================================================================
    echo [ERROR] Batch execution failed with error code: %errorlevel%
    echo ================================================================================
    echo.
    echo Please check the execution log for details.
    echo.
)

pause
