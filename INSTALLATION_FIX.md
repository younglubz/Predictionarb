# 🔧 Solução para Problemas de Instalação

## ⚠️ Problema Crítico

**Python 3.15 não é suportado ainda!**

Mesmo com Visual C++ Build Tools e Rust instalados, `pydantic-core` não consegue compilar porque:
- PyO3 (biblioteca Rust para Python) versão 0.26 só suporta até Python 3.14
- O código do `pydantic-core` usa APIs que não funcionam com Python 3.15
- Não há wheels pré-compilados para Python 3.15

## ✅ Solução Recomendada: Usar Python 3.11 ou 3.12

**Esta é a solução mais simples e confiável!**

## Soluções

### ✅ Opção 1: Usar Python 3.11 ou 3.12 (ALTAMENTE RECOMENDADO)

Python 3.11 e 3.12 têm wheels pré-compilados para todas as dependências e funcionam perfeitamente:

1. **Baixe Python 3.11 ou 3.12:**
   - https://www.python.org/downloads/
   - Escolha a versão 3.11.9 ou 3.12.7 (ou mais recente)

2. **Instale Python** (marque "Add Python to PATH" durante instalação)

3. **Verifique a versão:**
   ```powershell
   python --version
   ```
   Deve mostrar Python 3.11.x ou 3.12.x

4. **Crie um ambiente virtual (opcional mas recomendado):**
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

5. **Instale as dependências:**
   ```powershell
   pip install -r requirements.txt
   ```

6. **Pronto! Tudo deve funcionar!** 🎉

### ❌ Opção 2: Python 3.15 (NÃO FUNCIONA)

**Mesmo com Visual C++ Build Tools e Rust instalados, Python 3.15 não funciona porque:**
- PyO3 não suporta Python 3.15 ainda
- `pydantic-core` não compila
- Não há solução workaround viável

**Recomendação: Use Python 3.11 ou 3.12**

### ⚙️ Opção 3: Usar Apenas o CLI (Sem Dashboard Web)

Se você precisa usar Python 3.15, pode usar o sistema CLI sem o dashboard web:

1. **Instale apenas as dependências básicas:**
   ```powershell
   pip install requests python-dotenv rich httpx python-dateutil websockets
   ```

2. **Use o CLI diretamente:**
   ```powershell
   python main.py --monitor
   ```

3. **O dashboard web não funcionará**, mas o sistema de detecção de arbitragem funcionará normalmente.

## Status Atual

- ✅ `httpx` substituído por `aiohttp` (não precisa compilar)
- ✅ Visual C++ Build Tools instalado
- ✅ Rust instalado
- ❌ `pydantic-core` não compila com Python 3.15 (incompatibilidade PyO3)
- ❌ `fastapi` depende de `pydantic`
- ❌ Python 3.15 não é suportado ainda

## Recomendação Final

**🎯 USE PYTHON 3.11 OU 3.12**

Esta é a única solução que funciona completamente. Python 3.15 é muito novo e as bibliotecas ainda não foram atualizadas para suportá-lo.

### Passos Rápidos:

1. Baixe Python 3.11 ou 3.12
2. Instale (marque "Add to PATH")
3. Execute: `pip install -r requirements.txt`
4. Pronto! ✅

## Verificar Versão do Python

```powershell
python --version
```

Se mostrar 3.15, considere instalar Python 3.11 ou 3.12.

