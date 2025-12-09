"""Teste rápido da API Manifold"""
import asyncio
import httpx

async def test():
    async with httpx.AsyncClient(timeout=15.0) as client:
        url = "https://api.manifold.markets/v0/markets"
        params = {"limit": 5}
        response = await client.get(url, params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Tipo: {type(data)}")
            if isinstance(data, list):
                print(f"Mercados: {len(data)}")
                if data:
                    print(f"Primeiro mercado: {data[0].get('question', 'N/A')[:50]}")
            else:
                print(f"Resposta: {data}")
        else:
            print(f"Erro: {response.text[:200]}")

asyncio.run(test())

