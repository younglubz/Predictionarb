import asyncio
import httpx

async def test():
    async with httpx.AsyncClient(timeout=15.0) as client:
        url = "https://api.manifold.markets/v0/markets"
        params = {"limit": 10}
        response = await client.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"Total de mercados retornados: {len(data)}")
            for i, m in enumerate(data[:3]):
                print(f"\nMercado {i+1}:")
                print(f"  ID: {m.get('id')}")
                print(f"  Question: {m.get('question', 'N/A')[:50]}")
                print(f"  Probability: {m.get('probability')}")
                print(f"  Volume24h: {m.get('volume24Hours')}")
                print(f"  IsResolved: {m.get('isResolved')}")

asyncio.run(test())

