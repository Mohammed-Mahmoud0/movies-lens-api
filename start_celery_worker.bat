@echo off
echo ========================================
echo Starting Celery Worker
echo ========================================
cd /d "D:\Programming\ITI\django\advanced course\movies-lens-api"
call venv\Scripts\activate.bat
celery -A movies_api worker --loglevel=info --pool=solo
pause
