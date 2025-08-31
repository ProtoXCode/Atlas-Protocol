@echo off
setlocal enabledelayedexpansion
cd /d %~dp0
cd ..

:: In case anyone want's to compile the OCC files themselves.

echo "==========================="
echo "  Atlas OCC Runtime Setup  "
echo "==========================="
echo.

REM --- Vcpkg ---
if not exist vcpkg (
    echo [INFO] Cloning vcpkg...
    git clone https://github.com/microsoft/vcpkg.git
    if errorlevel 1 (
        echo [ERROR] Failed to clone vcpkg. Aborting.
        exit /b 1
    )
    cd vcpkg
    echo Bootstrapping vcpkg...
    call bootstrap-vcpkg.bat
    if errorlevel 1 (
        echo [ERROR] vcpkg bootstrap failed. Aborting.
        exit /b 1
    )
    echo Installing OpenCascade...
    vcpkg install opencascade:x64-windows
    if errorlevel 1 (
        echo [ERROR] Failed to install OpenCascade. Aborting.
        exit /b 1
    )
    cd ..
) else (
    echo [INFO] vcpkg already exists.
)

echo.
echo [INFO] Setup complete.

endlocal
