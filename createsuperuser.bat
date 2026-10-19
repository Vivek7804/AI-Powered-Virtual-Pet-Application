@echo off
echo Creating Django Superuser...
call .\venv\Scripts\activate.bat
python manage.py createsuperuser
pause
