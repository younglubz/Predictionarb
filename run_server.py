"""Script para executar o servidor FastAPI"""
import uvicorn
import sys
import os

if __name__ == "__main__":
    # Verifica se está usando Python 3.12
    if sys.version_info < (3, 12) or sys.version_info >= (3, 13):
        print("⚠️  Aviso: Recomendado usar Python 3.12")
        print(f"   Versão atual: {sys.version}")
    
    # Porta do ambiente (para Render, Railway, etc.) ou padrão 8000
    port = int(os.environ.get("PORT", 8000))
    # Host deve ser 0.0.0.0 para aceitar conexões externas
    host = os.environ.get("HOST", "0.0.0.0")
    # Reload apenas em desenvolvimento
    reload = os.environ.get("ENV", "production") == "development"
    
    print(f"🚀 Iniciando servidor em {host}:{port}")
    print(f"   Ambiente: {'desenvolvimento' if reload else 'produção'}")
    
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

