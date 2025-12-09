# -*- coding: utf-8 -*-
"""Teste direto dos mercados"""
import asyncio
import httpx

async def test_markets():
    print("\n=== TESTANDO ENDPOINTS DO BACKEND ===\n")
    
    import traceback
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Teste 1: Stats
        print("1. Testando /stats...")
        try:
            response = await client.get("http://localhost:8000/stats")
            data = response.json()
            print(f"   ✓ Status: {response.status_code}")
            print(f"   ✓ Total mercados: {data.get('total_markets', 0)}")
            print(f"   ✓ Oportunidades: {data.get('opportunities_count', 0)}")
            print(f"   ✓ Exchanges: {list(data.get('by_exchange', {}).keys())}")
        except Exception as e:
            print(f"   ✗ Erro: {e}")
            traceback.print_exc()
        
        # Teste 2: Markets
        print("\n2. Testando /markets...")
        try:
            response = await client.get("http://localhost:8000/markets")
            data = response.json()
            print(f"   ✓ Status: {response.status_code}")
            print(f"   ✓ Count: {data.get('count', 0)}")
            print(f"   ✓ Markets array length: {len(data.get('markets', []))}")
            print(f"   ✓ Exchanges: {data.get('exchanges', [])}")
            
            if data.get('error'):
                print(f"   ✗ ERRO NO BACKEND: {data['error']}")
            
            # Mostra primeiros 3 mercados
            markets = data.get('markets', [])
            if markets:
                print(f"\n   Primeiros 3 mercados:")
                for i, m in enumerate(markets[:3]):
                    print(f"   {i+1}. [{m.get('exchange')}] {m.get('question', '')[:50]}...")
            else:
                print("   ⚠ NENHUM MERCADO RETORNADO!")
        except Exception as e:
            print(f"   ✗ Erro: {e}")
            traceback.print_exc()
        
        # Teste 3: Opportunities
        print("\n3. Testando /opportunities...")
        try:
            response = await client.get("http://localhost:8000/opportunities")
            data = response.json()
            print(f"   ✓ Status: {response.status_code}")
            print(f"   ✓ Count: {data.get('count', 0)}")
            
            opps = data.get('opportunities', [])
            if opps:
                print(f"\n   Primeiras 3 oportunidades:")
                for i, opp in enumerate(opps[:3]):
                    print(f"   {i+1}. {opp.get('profit_pct', 0)*100:.2f}% - {opp.get('buy', {}).get('exchange')} → {opp.get('sell', {}).get('exchange')}")
            else:
                print("   ⚠ Nenhuma oportunidade encontrada")
        except Exception as e:
            print(f"   ✗ Erro: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_markets())

