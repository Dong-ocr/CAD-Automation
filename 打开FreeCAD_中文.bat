@echo off
chcp 65001 >nul
set LANG=zh_CN
set LC_ALL=zh_CN.UTF-8
set FREECAD_USE_LANG=zh_CN
start "" "%~dp0\FreeCAD\FreeCAD_1.1.1-Windows-x86_64-py311\bin\freecad.exe"
