# Script para iniciar o monitor diário automático
Write-Host "`n📅 Iniciando Monitor Diário de Arbitragem...`n" -ForegroundColor Cyan

# Verifica se Python está instalado
$pythonCmd = $null
if (Get-Command "py" -ErrorAction SilentlyContinue) {
    $pythonCmd = "py -3.12"
    Write-Host "✓ Python 3.12 encontrado" -ForegroundColor Green
} elseif (Get-Command "python" -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
    Write-Host "✓ Python encontrado" -ForegroundColor Green
} else {
    Write-Host "❌ Python não encontrado!" -ForegroundColor Red
    Write-Host "Instale Python 3.12 primeiro: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Instala schedule se necessário
Write-Host "`nVerificando dependências..." -ForegroundColor Yellow
& $pythonCmd -m pip install schedule --quiet

Write-Host "`n════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Monitor Diário de Arbitragem" -ForegroundColor Green
Write-Host "════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "`nHorários de verificação automática:" -ForegroundColor White
Write-Host "  • 09:00 - Manhã" -ForegroundColor White
Write-Host "  • 15:00 - Tarde" -ForegroundColor White
Write-Host "  • 21:00 - Noite" -ForegroundColor White
Write-Host "`n════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "`nPressione Ctrl+C para parar o monitor`n" -ForegroundColor Yellow

# Executa monitor
& $pythonCmd daily_monitor.py

