import asyncio
from monitor import ArbitrageMonitor
async def test():
    m = ArbitrageMonitor()
    markets = await m.fetch_all_markets()
    print(f"Total: {len(markets)} mercados")
asyncio.run(test())
