import sys
import asyncio
from monitor import ArbitrageMonitor

async def test():
    m = ArbitrageMonitor()
    print("TESTE: Monitor criado", flush=True)
    sys.stdout.flush()
    markets = await m.fetch_all_markets()
    print(f"TESTE: Total {len(markets)} mercados", flush=True)
    sys.stdout.flush()

asyncio.run(test())
