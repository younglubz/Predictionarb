"""Testa APIs diretamente"""
import asyncio
import httpx
import json

async def test_predictit():
    print("\n=== Testando PredictIt ===")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = "https://www.predictit.org/api/Market/GetAllMarkets"
            response = await client.get(url)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Tipo: {type(data)}")
                if isinstance(data, list):
                    print(f"Mercados encontrados: {len(data)}")
                    if data:
                        print(f"Exemplo: {json.dumps(data[0], indent=2)[:200]}")
                else:
                    print(f"Dados: {json.dumps(data, indent=2)[:500]}")
            else:
                print(f"Resposta: {response.text[:200]}")
    except Exception as e:
        print(f"Erro: {e}")

async def test_kalshi():
    print("\n=== Testando Kalshi ===")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = "https://trading-api.kalshi.com/trade-api/v2/events"
            params = {"limit": 10, "status": "open"}
            response = await client.get(url, params=params)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Dados: {json.dumps(data, indent=2)[:500]}")
            else:
                print(f"Resposta: {response.text[:200]}")
    except Exception as e:
        print(f"Erro: {e}")

async def test_augur():
    print("\n=== Testando Augur ===")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Tenta diferentes URLs
            urls = [
                "https://api.augur.net/markets",
                "https://thegraph.com/hosted-service/subgraph/augurproject/augur",
                "https://augur.net/api/markets"
            ]
            for url in urls:
                try:
                    response = await client.get(url)
                    print(f"URL: {url}")
                    print(f"Status: {response.status_code}")
                    if response.status_code == 200:
                        print(f"Sucesso!")
                        break
                except:
                    print(f"URL: {url} - Falhou")
    except Exception as e:
        print(f"Erro: {e}")

async def test_polymarket():
    print("\n=== Testando Polymarket ===")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = "https://clob.polymarket.com/markets"
            params = {"active": "true", "limit": 5}
            response = await client.get(url, params=params, headers={"Accept": "application/json"})
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Tipo: {type(data)}")
                if isinstance(data, list):
                    print(f"Mercados: {len(data)}")
                else:
                    print(f"Chaves: {list(data.keys())[:10] if isinstance(data, dict) else 'N/A'}")
    except Exception as e:
        print(f"Erro: {e}")

async def main():
    await test_polymarket()
    await test_predictit()
    await test_kalshi()
    await test_augur()

if __name__ == "__main__":
    asyncio.run(main())

