"""Script para executar o servidor FastAPI"""
import uvicorn
import sys

if __name__ == "__main__":
    # Verifica se está usando Python 3.12
    if sys.version_info < (3, 12) or sys.version_info >= (3, 13):
        print("⚠️  Aviso: Recomendado usar Python 3.12")
        print(f"   Versão atual: {sys.version}")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

