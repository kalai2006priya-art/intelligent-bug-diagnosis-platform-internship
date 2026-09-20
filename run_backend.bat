@echo off
title Bug Diagnosis Platform - Backend
cd /d "%~dp0backend"
python -m uvicorn app.main:app --reload --port 8000
pause
