@echo off
echo Stopping CAD Server...
if exist server.pid (
    set /p PID=<server.pid
    taskkill /PID %PID% /F 2>nul
    del server.pid
)
taskkill /f /im python.exe /fi 
WINDOWTITLE
eq
server.py 2>nul
echo Done.
