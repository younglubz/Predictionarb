@echo off
title Prediction Arbitrage - Iniciando Sistema
color 0A

echo.
echo ================================================================
echo           PREDICTION MARKET ARBITRAGE
echo           Sistema de Arbitragem em Tempo Real
echo ================================================================
echo.
echo Iniciando sistema...
echo.

REM Navega para o diretório do projeto
cd /d "%~dp0"

echo [1/3] Iniciando Backend (FastAPI)...
start "Backend - FastAPI" cmd /k "py -3.12 run_server.py"
timeout /t 5 /nobreak >nul

echo [2/3] Iniciando Frontend (React)...
start "Frontend - React" cmd /k "cd frontend && npm start"
timeout /t 3 /nobreak >nul

echo [3/3] Abrindo Dashboard...
timeout /t 15 /nobreak >nul
start http://localhost:3000

echo.
echo ================================================================
echo           SISTEMA INICIADO COM SUCESSO!
echo ================================================================
echo.
echo URLs de Acesso:
echo   Dashboard: http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo Aguardando 20 segundos para processar...
timeout /t 20 /nobreak >nul
echo.
echo Sistema pronto! Aproveite!
echo.
pause

