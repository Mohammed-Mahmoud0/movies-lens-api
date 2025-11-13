@echo off
echo ========================================
echo Starting Flower (Celery Monitoring)
echo ========================================
echo Flower will be available at: http://localhost:5555
echo ========================================
cd /d "D:\Programming\ITI\django\advanced course\movies-lens-api"
call venv\Scripts\activate.bat
celery -A movies_api flower
pause
