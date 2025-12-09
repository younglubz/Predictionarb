# Script para instalar Python e executar o projeto
Write-Host "=== Prediction Market Arbitrage Bot ===" -ForegroundColor Cyan
Write-Host ""

# Verifica se Python está instalado
$pythonInstalled = $false
$pythonCmd = $null

# Tenta encontrar Python
$paths = @("python", "python3", "py")
foreach ($cmd in $paths) {
    try {
        $result = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $result -notmatch "nao foi encontrado|not found") {
            $pythonCmd = $cmd
            $pythonInstalled = $true
            Write-Host "Python encontrado: $cmd $result" -ForegroundColor Green
            break
        }
    } catch {
        # Continua procurando
    }
}

# Se não encontrou, tenta instalar
if (-not $pythonInstalled) {
    Write-Host "Python nao esta instalado." -ForegroundColor Yellow
    Write-Host "Tentando instalar via winget..." -ForegroundColor Yellow
    
    try {
        winget install --id Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
        Write-Host "Python instalado com sucesso!" -ForegroundColor Green
        Write-Host "Por favor, feche e reabra o terminal, depois execute novamente." -ForegroundColor Yellow
        exit 0
    } catch {
        Write-Host ""
        Write-Host "Nao foi possivel instalar automaticamente." -ForegroundColor Red
        Write-Host ""
        Write-Host "Por favor, instale Python manualmente:" -ForegroundColor Yellow
        Write-Host "1. Via winget: winget install Python.Python.3.11" -ForegroundColor Cyan
        Write-Host "2. Ou baixe de: https://www.python.org/downloads/" -ForegroundColor Cyan
        Write-Host "3. Certifique-se de marcar 'Add Python to PATH' durante a instalacao" -ForegroundColor Cyan
        exit 1
    }
}

# Instala dependências
Write-Host ""
Write-Host "Instalando dependencias..." -ForegroundColor Yellow
& $pythonCmd -m pip install --quiet --upgrade pip
& $pythonCmd -m pip install --quiet -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "Dependencias instaladas!" -ForegroundColor Green
} else {
    Write-Host "Erro ao instalar dependencias" -ForegroundColor Red
    exit 1
}

# Executa o projeto
Write-Host ""
Write-Host "=== Executando projeto ===" -ForegroundColor Green
Write-Host ""
& $pythonCmd main.py
