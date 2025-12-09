# Script para executar o projeto
Write-Host "Buscando Python..." -ForegroundColor Yellow

# Tenta diferentes formas de encontrar Python
$pythonCmd = $null

# 1. Tenta python3
try {
    $result = Get-Command python3 -ErrorAction SilentlyContinue
    if ($result) {
        $pythonCmd = "python3"
        Write-Host "Python encontrado: python3" -ForegroundColor Green
    }
} catch {}

# 2. Tenta py launcher
if (-not $pythonCmd) {
    try {
        $result = Get-Command py -ErrorAction SilentlyContinue
        if ($result) {
            $pythonCmd = "py"
            Write-Host "Python encontrado: py" -ForegroundColor Green
        }
    } catch {}
}

# 3. Busca em locais comuns
if (-not $pythonCmd) {
    $commonPaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe",
        "C:\Python*\python.exe",
        "C:\Program Files\Python*\python.exe",
        "C:\Program Files (x86)\Python*\python.exe"
    )
    
    foreach ($path in $commonPaths) {
        $found = Get-ChildItem $path -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            $pythonCmd = $found.FullName
            Write-Host "Python encontrado: $pythonCmd" -ForegroundColor Green
            break
        }
    }
}

if (-not $pythonCmd) {
    Write-Host "`nPython não encontrado!" -ForegroundColor Red
    Write-Host "`nInstale Python primeiro:" -ForegroundColor Yellow
    Write-Host "  winget install Python.Python.3.11" -ForegroundColor Cyan
    Write-Host "  ou baixe de: https://www.python.org/downloads/" -ForegroundColor Cyan
    exit 1
}

# Verifica se as dependências estão instaladas
Write-Host "`nVerificando dependências..." -ForegroundColor Yellow
try {
    $test = & $pythonCmd -c "import aiohttp, rich" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Instalando dependências..." -ForegroundColor Yellow
        & $pythonCmd -m pip install -q -r requirements.txt
    } else {
        Write-Host "Dependências OK!" -ForegroundColor Green
    }
} catch {
    Write-Host "Instalando dependências..." -ForegroundColor Yellow
    & $pythonCmd -m pip install -q -r requirements.txt
}

# Executa o projeto
Write-Host "`nExecutando projeto..." -ForegroundColor Green
& $pythonCmd main.py

