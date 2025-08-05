@echo off
echo Installing Twitter API dependencies...
echo.

REM Install required packages
python -m pip install tweepy python-dotenv pandas

REM Test the API connection
echo.
echo Testing API connection...
python test_api_connection.py

pause