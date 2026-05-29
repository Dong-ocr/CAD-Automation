#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""FreeCAD Chinese locale fix - configures Simplified Chinese UI"""
import os, sys, shutil

FC_DIR = os.path.dirname(r"E:\CAD自动化制图\FreeCAD\FreeCAD_1.1.1-Windows-x86_64-py311\bin\FreeCADCmd.exe")
# Actually compute it properly
FC_BIN = r"E:\CAD自动化制图\FreeCAD\FreeCAD_1.1.1-Windows-x86_64-py311\bin"
FC_ROOT = os.path.dirname(FC_BIN)

# Fix user.cfg
user_cfg_dir = os.path.join(os.environ.get("APPDATA",""), "FreeCAD")
os.makedirs(user_cfg_dir, exist_ok=True)

# Check existing translations
translations_dir = os.path.join(FC_ROOT, "translations")
ts_dir = os.path.join(FC_ROOT, "share", "FreeCAD", "translations")
found_ts = []
for d in [translations_dir, ts_dir]:
    if os.path.isdir(d):
        for f in os.listdir(d):
            if "zh" in f.lower():
                found_ts.append(os.path.join(d, f))

print("Chinese translation files found:")
for f in found_ts:
    sz = os.path.getsize(f) // 1024
    print(f"  {f} ({sz}KB)")

# Create user.cfg with Chinese locale
user_cfg_path = os.path.join(user_cfg_dir, "user.cfg")
import configparser
cfg = configparser.ConfigParser()
cfg.optionxform = str  # preserve case

if os.path.exists(user_cfg_path):
    cfg.read(user_cfg_path, encoding="utf-8")
else:
    cfg["General"] = {}
    cfg["Preferences"] = {}

cfg["General"]["Language"] = "Chinese"
cfg["General"]["LANG"] = "zh_CN"
cfg["Preferences"]["Language"] = "Chinese"
cfg["Preferences"]["Locale"] = "zh_CN"
cfg["Preferences"]["DecimalPoint"] = "."

# Also set UI-specific settings
cfg["General"]["UiLanguage"] = "zh_CN"
cfg["General"]["UiLanguageFromEnv"] = "False"

with open(user_cfg_path, "w", encoding="utf-8") as f:
    cfg.write(f)

print(f"\nUpdated: {user_cfg_path}")

# Create batch file to launch FreeCAD in Chinese
bat_content = """@echo off
chcp 65001 >nul
set LANG=zh_CN
set LC_ALL=zh_CN.UTF-8
set FREECAD_USE_LANG=zh_CN
start "" "%~dp0\\FreeCAD\\FreeCAD_1.1.1-Windows-x86_64-py311\\bin\\freecad.exe"
"""

with open(r"E:\CAD自动化制图\打开FreeCAD_中文.bat", "w", encoding="utf-8") as f:
    f.write(bat_content)

print("Created: 打开FreeCAD_中文.bat")

# Verify
print("\n=== FreeCAD Chinese locale check ===")
import subprocess
result = subprocess.run([os.path.join(FC_BIN, "FreeCADCmd.exe"), "-c",
    "import FreeCAD; print('Language:', FreeCAD.ConfigGet('Language'))"],
    capture_output=True, text=True, timeout=30)
print(result.stdout.strip())
print("Done")
