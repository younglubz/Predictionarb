# 🚀 Solução Rápida - Python 3.15 Não Funciona

## ⚠️ Problema

Você está usando **Python 3.15**, que é muito novo. As bibliotecas (`pydantic-core`, `fastapi`) ainda não suportam Python 3.15.

## ✅ Solução (5 minutos)

### 1. Instale Python 3.12

- Baixe: https://www.python.org/downloads/release/python-3127/
- Durante instalação: **MARQUE "Add Python to PATH"**
- Instale normalmente

### 2. Verifique

```powershell
python --version
```

Deve mostrar: `Python 3.12.x`

### 3. Instale Dependências

```powershell
pip install -r requirements.txt
```

### 4. Pronto! 🎉

Agora você pode usar:
- `python run_server.py` - Backend API
- `cd frontend && npm start` - Frontend

## Por que Python 3.15 não funciona?

- PyO3 (Rust para Python) só suporta até Python 3.14
- `pydantic-core` precisa compilar código Rust
- Não há wheels pré-compilados para Python 3.15
- Mesmo com Visual C++ e Rust instalados, não compila

## Alternativa: Usar CLI sem Dashboard

Se você **realmente** precisa usar Python 3.15:

```powershell
# Instale apenas dependências básicas
pip install requests python-dotenv rich httpx python-dateutil websockets

# Use o CLI
python main.py --monitor
```

O dashboard web não funcionará, mas a detecção de arbitragem funcionará.

---

**Recomendação: Use Python 3.12. É mais fácil e tudo funciona!** ✅

