# Script para iniciar o frontend
Write-Host "=== Iniciando Frontend React ===" -ForegroundColor Green
Write-Host ""

# Verifica Node.js
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodeCmd) {
    Write-Host "Node.js não encontrado! Instale Node.js 16+" -ForegroundColor Red
    exit 1
}

Write-Host "Node.js encontrado: $($nodeCmd.Source)" -ForegroundColor Green

# Navega para o diretório do frontend
Set-Location frontend

# Verifica se node_modules existe
if (-not (Test-Path "node_modules")) {
    Write-Host "`nInstalando dependências do frontend..." -ForegroundColor Yellow
    npm install
}

# Inicia o servidor de desenvolvimento
Write-Host "`n=== Iniciando servidor de desenvolvimento ===" -ForegroundColor Green
Write-Host "Frontend disponível em: http://localhost:3000" -ForegroundColor Cyan
Write-Host "`nPressione Ctrl+C para parar o servidor`n" -ForegroundColor Yellow

npm start

