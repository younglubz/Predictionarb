import asyncio
import sys
from exchanges.mock import MockExchange

async def test():
    sys.stdout.write("TESTE: Iniciando\n")
    sys.stdout.flush()
    m = MockExchange()
    sys.stdout.write(f"TESTE: Exchange criado: {m.name}\n")
    sys.stdout.flush()
    markets = await m.fetch_markets()
    sys.stdout.write(f"TESTE: Retornou {len(markets)} mercados\n")
    sys.stdout.flush()
    return markets

result = asyncio.run(test())
print(f"RESULTADO FINAL: {len(result)} mercados")
