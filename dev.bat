@echo off
REM Development startup script for Windows
REM Double-click to run or execute from cmd

cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "dev.ps1"
pause
