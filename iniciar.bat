@echo off
REM Inicia backend (FastAPI/uvicorn) e frontend (Vite) em janelas separadas.
REM Segue as premissas de Anotacoes.txt: uvicorn --host 0.0.0.0 --port 8002
REM (acesso via rede local) e npm run dev na pasta frontend.

cd /d "%~dp0"

if not exist venv\Scripts\activate.bat (
    echo [ERRO] venv nao encontrado. Rode: python -m venv venv ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)

if not exist .env (
    echo [ERRO] .env nao encontrado. Copie .env.example para .env e preencha JWT_SECRET_KEY.
    pause
    exit /b 1
)

if not exist frontend\node_modules (
    echo [ERRO] frontend\node_modules nao encontrado. Rode: cd frontend ^&^& npm install
    pause
    exit /b 1
)

echo Iniciando backend (uvicorn) em nova janela...
start "Gossipy Watchman - Backend" cmd /k "cd /d "%~dp0" && venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 0.0.0.0 --port 8002"

echo Iniciando frontend (Vite) em nova janela...
start "Gossipy Watchman - Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo Backend:  http://localhost:8002/api/v1/health
echo Frontend: http://localhost:5174
echo.
