@echo off
echo Starting AI Virtual Pet Development Server...
call .\venv\Scripts\activate.bat
python manage.py runserver
pause
