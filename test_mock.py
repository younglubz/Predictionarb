import asyncio
from exchanges.mock import MockExchange
m = MockExchange()
markets = asyncio.run(m.fetch_markets())
print(f"Mock encontrou {len(markets)} mercados")
for market in markets[:2]:
    print(f"  - {market.question[:50]}... ({market.outcome}) @ ${market.price}")
