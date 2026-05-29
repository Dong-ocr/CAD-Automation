@echo off
start /B python server.py 8780
echo CAD Server started on http://localhost:8780
echo.
echo Open your browser to: http://localhost:8780/interior_cad.html
echo.
echo Press any key to stop the server...
pause >nul
taskkill /f /im python.exe 2>nul
