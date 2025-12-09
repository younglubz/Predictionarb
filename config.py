"""Configurações do sistema de arbitragem"""
import os
from dotenv import load_dotenv

load_dotenv()

# Intervalos e thresholds
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", 20))  # segundos (reduzido para dados mais atualizados)
MIN_ARBITRAGE_PROFIT = float(os.getenv("MIN_ARBITRAGE_PROFIT", 0.02))  # 2% (OTIMIZADO - apenas oportunidades reais)
MIN_LIQUIDITY = float(os.getenv("MIN_LIQUIDITY", 100))  # USD (OTIMIZADO - mercados com liquidez real)

# Taxas estimadas por exchange (em %)
EXCHANGE_FEES = {
    "polymarket": 0.02,  # 2%
    "manifold": 0.00,    # 0% - Manifold nao cobra taxas
    "predictit": 0.10,   # 10% - PredictIt fee (5% compra + 5% venda)
    "kalshi": 0.07,      # 7% - Kalshi exchange fee
    "polyrouter_polymarket": 0.02,
    "polyrouter_kalshi": 0.07,
    "polyrouter_manifold": 0.00,
    "polyrouter_predictit": 0.10,
    "augur": 0.01,       # 1%
}

# Gas fees estimados (para blockchains)
GAS_FEES = {
    "polymarket": 0.001,  # ETH
    "augur": 0.001,       # ETH
}

# APIs
API_ENDPOINTS = {
    "polymarket": "https://clob.polymarket.com",
    "augur": "https://api.augur.net",
    "predictit": "https://www.predictit.org/api",
    "kalshi": "https://trading-api.kalshi.com/trade-api/v2",
}

