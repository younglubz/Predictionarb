# -*- coding: utf-8 -*-
"""Teste simples da Kalshi"""
import asyncio
from exchanges.kalshi_v2 import KalshiV2Exchange

async def test():
    print("\nTestando Kalshi...\n")
    
    exchange = KalshiV2Exchange()
    print(f"URL: {exchange.api_url}")
    
    markets = await exchange.fetch_markets()
    
    print(f"\nMercados retornados: {len(markets)}")
    
    if markets:
        print("\nPrimeiros 5 mercados:")
        for m in markets[:5]:
            print(f"  - {m.question[:60]}... (${m.price:.3f})")
    
    return len(markets)

if __name__ == "__main__":
    count = asyncio.run(test())
    
    if count > 0:
        print(f"\n✓ Kalshi funcionando com {count} mercados!")
    else:
        print("\nX Kalshi retornou 0 mercados")

