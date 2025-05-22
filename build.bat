@echo off
REM Build js_obfuscator_gui.exe using PyInstaller

REM 检查PyInstaller是否已安装
where pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未检测到PyInstaller，请先运行: pip install pyinstaller
    pause
    exit /b 1
)

REM 打包为单文件、无控制台窗口
pyinstaller --onefile --noconsole js_obfuscator_gui.py

echo.
echo [完成] 可执行文件已生成于 dist\js_obfuscator_gui.exe
pause 