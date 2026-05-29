$key = "HKCU:\SOFTWARE\Autodesk\AutoCAD\R25.0\ACAD-8101"
New-Item -Path $key -Force -ErrorAction SilentlyContinue | Out-Null
Set-ItemProperty -Path $key -Name "CurVer" -Value "ACAD-8101" -Force
Set-ItemProperty -Path $key -Name "FixedRootFolder" -Value "F:\AutoCAD 2025" -Force
Set-ItemProperty -Path $key -Name "RoamableRootFolder" -Value "F:\AutoCAD 2025" -Force
Set-ItemProperty -Path $key -Name "ProgramDir" -Value "F:\AutoCAD 2025" -Force
Set-ItemProperty -Path $key -Name "InstalledLanguageIds" -Value "804" -Force
Write-Host "Registry done!"
