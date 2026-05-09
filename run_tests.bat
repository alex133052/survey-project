@echo off
echo ====================================
echo Setting up environment...
echo ====================================

REM Создаём виртуальное окружение если нет
if not exist .venv (
    echo Creating virtual environment...
    uv venv
)

REM Устанавливаем pytest через uv pip
echo Installing pytest...
uv pip install pytest

REM Запускаем тесты
echo.
echo ====================================
echo Running tests...
echo ====================================
.venv\Scripts\pytest.exe -v

echo.
echo ====================================
pause