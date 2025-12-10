# -*- coding: utf-8 -*-
"""Testa estrutura real dos mercados da Kalshi"""
import asyncio
from exchanges.kalshi_v2 import KalshiV2Exchange

async def test_kalshi():
    exchange = KalshiV2Exchange()
    markets = await exchange.fetch_markets()
    
    print(f"\nTotal de mercados: {len(markets)}\n")
    
    # Mostra primeiros 10 mercados com suas questions
    print("Primeiros 10 mercados da Kalshi:")
    print("=" * 80)
    for i, m in enumerate(markets[:10], 1):
        print(f"\n{i}. Exchange: {m.exchange}")
        print(f"   Question: {m.question}")
        print(f"   Outcome: {m.outcome}")
        print(f"   Price: ${m.price:.3f}")
        print(f"   Market ID: {m.market_id}")
        print(f"   URL: {m.url}")

if __name__ == "__main__":
    asyncio.run(test_kalshi())

