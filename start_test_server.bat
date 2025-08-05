@echo off
echo ╔══════════════════════════════════════════════════════╗
echo ║        Miles Deutscher AI - Starting Test Server     ║
echo ╚══════════════════════════════════════════════════════╝
echo.
echo Installing dependencies...
pip install flask flask-cors

echo.
echo Starting server...
echo.
echo Server will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python local_server.py

pause