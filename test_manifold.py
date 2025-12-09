import asyncio
from exchanges.manifold import ManifoldExchange

async def test():
    ex = ManifoldExchange()
    markets = await ex.fetch_markets()
    print(f'Mercados Manifold: {len(markets)}')
    if markets:
        print(f'Exemplo: {markets[0].question[:50]}')

asyncio.run(test())

