# -*- coding: utf-8 -*-
"""Otimizacao de performance da API"""
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from functools import lru_cache
import time

# Cache para endpoints
@lru_cache(maxsize=128)
def get_cached_stats(timestamp: int):
    """Cache de stats por 30 segundos"""
    # Implementacao real em api.py
    pass

# Adicionar ao api.py:
"""
# Compressao GZIP
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Cache de respostas
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend())

@app.get("/stats")
@cache(expire=30)  # Cache por 30 segundos
async def get_stats():
    # Codigo existente
    pass

@app.get("/opportunities")  
@cache(expire=10)  # Cache por 10 segundos
async def get_opportunities():
    # Codigo existente
    pass
"""

print("Adicione estas otimizacoes ao api.py para melhorar performance")

