import asyncio
from monitor import ArbitrageMonitor
from rich.console import Console

console = Console()

async def test():
    m = ArbitrageMonitor()
    console.print(f"Exchanges configuradas: {[e.name for e in m.exchanges]}")
    markets = await m.fetch_all_markets()
    console.print(f"Total coletado: {len(markets)} mercados")

asyncio.run(test())
