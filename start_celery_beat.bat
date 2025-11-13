@echo off
cd /d "D:\Programming\ITI\django\advanced course\movies-lens-api"
call venv\Scripts\activate.bat
celery -A movies_api beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
pause
