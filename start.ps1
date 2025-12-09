# Script para iniciar o servidor backend
Write-Host "=== Iniciando Prediction Market Arbitrage Dashboard ===" -ForegroundColor Green
Write-Host ""

# Verifica Python 3.12 (recomendado)
$pythonCmd = Get-Command py -ErrorAction SilentlyContinue
if ($pythonCmd) {
    # Tenta usar Python 3.12
    $python312 = & py -3.12 --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $pythonCmd = "py -3.12"
        Write-Host "Usando Python 3.12 via py launcher" -ForegroundColor Green
    } else {
        # Fallback para python padrão
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if (-not $pythonCmd) {
            Write-Host "Python 3.12 não encontrado! Use 'py -3.12' ou instale Python 3.12" -ForegroundColor Red
            exit 1
        }
        Write-Host "Python encontrado: $($pythonCmd.Source)" -ForegroundColor Yellow
        Write-Host "⚠️  Recomendado usar Python 3.12 (py -3.12)" -ForegroundColor Yellow
    }
} else {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        Write-Host "Python não encontrado! Instale Python 3.12" -ForegroundColor Red
        exit 1
    }
    Write-Host "Python encontrado: $($pythonCmd.Source)" -ForegroundColor Yellow
    Write-Host "⚠️  Recomendado usar Python 3.12" -ForegroundColor Yellow
}

# Instala dependências se necessário
Write-Host "`nVerificando dependências..." -ForegroundColor Yellow
try {
    if ($pythonCmd -is [string] -and $pythonCmd -like "py -3.12*") {
        $test = & py -3.12 -c "import fastapi, uvicorn" 2>&1
        $pipCmd = "py -3.12 -m pip"
    } else {
        $test = & $pythonCmd -c "import fastapi, uvicorn" 2>&1
        $pipCmd = "$pythonCmd -m pip"
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Instalando dependências..." -ForegroundColor Yellow
        Invoke-Expression "$pipCmd install -q -r requirements.txt"
    } else {
        Write-Host "Dependências OK!" -ForegroundColor Green
    }
} catch {
    Write-Host "Instalando dependências..." -ForegroundColor Yellow
    if ($pythonCmd -is [string] -and $pythonCmd -like "py -3.12*") {
        & py -3.12 -m pip install -q -r requirements.txt
    } else {
        & $pythonCmd -m pip install -q -r requirements.txt
    }
}

# Inicia o servidor
Write-Host "`n=== Iniciando servidor backend ===" -ForegroundColor Green
Write-Host "Servidor disponível em: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs disponível em: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "`nPressione Ctrl+C para parar o servidor`n" -ForegroundColor Yellow

if ($pythonCmd -is [string] -and $pythonCmd -like "py -3.12*") {
    & py -3.12 run_server.py
} else {
    & $pythonCmd run_server.py
}

