import asyncio
from exchanges.mock import MockExchange
m = MockExchange()
r = asyncio.run(m.fetch_markets())
print(f"Mock retornou: {len(r)} mercados")
for i, market in enumerate(r[:2]):
    print(f"  {i+1}. {market.question[:50]}... ({market.outcome}) @ ${market.price}")
