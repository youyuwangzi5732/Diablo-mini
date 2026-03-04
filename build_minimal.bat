@echo off
chcp 65001 >nul
echo ========================================
echo   Diablo Mini - 最小化打包
echo ========================================
echo.

echo 此脚本将生成最小化的可执行文件
echo 预计大小: 15-25 MB
echo.

pause

echo [1/3] 清理旧文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo [2/3] 开始最小化打包...
pyinstaller build_minimal.spec --clean --noconfirm

echo [3/3] 检查结果...
if exist "dist\DiabloMini.exe" (
    echo.
    echo ========================================
    echo   打包成功！
    echo ========================================
    echo.
    for %%I in ("dist\DiabloMini.exe") do (
        set size=%%~zI
        set /a sizeMB=%%~zI/1048576
    )
    echo 文件: dist\DiabloMini.exe
    echo 大小: %sizeMB% MB
    echo.
) else (
    echo 打包失败！
)

pause
