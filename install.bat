@echo off
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python이 설치되어 있지 않습니다.
    exit /b 1
)

pip install .
git-commit-generator --install-hooks