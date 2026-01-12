@echo off
echo ========================================
echo  PanditGo Admin Backend Setup
echo ========================================
echo.

cd backend

echo Installing dependencies...
npm install

if %errorlevel% neq 0 (
    echo ❌ npm install failed. Please check Node.js installation.
    pause
    exit /b 1
)

echo.
echo ✅ Dependencies installed successfully!
echo.
echo Starting PanditGo Backend Server...
echo Server will run on http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

npm start