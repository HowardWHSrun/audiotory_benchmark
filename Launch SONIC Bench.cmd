@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel% equ 0 (
  py -3 scripts\launch_bench_app.py %*
) else (
  python scripts\launch_bench_app.py %*
)
if errorlevel 1 pause
