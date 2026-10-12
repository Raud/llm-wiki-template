@echo off
rem Launcher for the wiki tools.
rem
rem It exists for one non-obvious reason: `python` on PATH can be a Microsoft Store execution
rem alias - a stub that answers nothing useful. So the interpreter is probed, not just located.
rem This is the only place that probe lives; per-tool copies are how it drifted before.
rem
rem   wiki lint [args]   structural lint (read-only)
rem   wiki norm [args]   canonicalize line-oriented JSON registries (mutating)
rem
rem If Python is unavailable, `lint` is skipped (the wiki works without it) and any other tool
rem fails loudly, because those genuinely require Python.
setlocal
set "PROBE=import sys;sys.exit(0 if sys.version_info>=(3,9) else 3)"

py -3 -c "%PROBE%" >nul 2>nul
if not errorlevel 1 goto use_py

python -c "%PROBE%" >nul 2>nul
if not errorlevel 1 goto use_python

goto no_python

:use_py
py -3 "%~dp0wiki.py" %*
exit /b %errorlevel%

:use_python
python "%~dp0wiki.py" %*
exit /b %errorlevel%

:no_python
if /i "%~1"=="lint" (
  echo Python 3.9+ not found - lint skipped. The wiki works without it.
  exit /b 0
)
echo Python 3.9+ not found - the wiki tools require Python 3.9+.
exit /b 2
