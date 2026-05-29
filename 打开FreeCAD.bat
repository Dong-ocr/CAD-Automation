@echo off
chcp 65001 >nul
echo 启动 FreeCAD 中文版...
set LANG=zh_CN
set LC_ALL=zh_CN
start "" "E:\CAD自动化制图\FreeCAD\FreeCAD_1.1.1-Windows-x86_64-py311\bin\freecad.exe" "E:\CAD自动化制图\output\professional\floor_plan_gbt.dxf"
