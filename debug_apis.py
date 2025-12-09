import asyncio
import aiohttp
from rich.console import Console
console = Console()
async def test():
    console.print("[yellow]Testando APIs...[/yellow]")
    try:
        async with aiohttp.ClientSession() as s:
            r = await s.get("https://www.predictit.org/api/Market/GetAllMarkets", timeout=aiohttp.ClientTimeout(total=10))
            console.print(f"PredictIt Status: {r.status}")
            if r.status == 200:
                d = await r.json()
                console.print(f"Tipo: {type(d)}, Tamanho: {len(d) if isinstance(d, list) else 'N/A'}")
    except Exception as e:
        console.print(f"[red]Erro: {e}[/red]")
asyncio.run(test())
