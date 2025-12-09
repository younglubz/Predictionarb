# -*- coding: utf-8 -*-
"""Teste da integracao PredictIt v2"""
import asyncio
from exchanges.predictit_v2 import PredictItV2Exchange
from rich.console import Console
from rich.table import Table

console = Console()


async def test_predictit():
    console.print("\n[bold cyan]Testando PredictIt API v2[/bold cyan]\n")
    console.print("[yellow]API: https://www.predictit.org/api/marketdata/all/[/yellow]\n")
    
    exchange = PredictItV2Exchange()
    
    # Busca mercados
    console.print("[yellow]Buscando mercados...[/yellow]")
    markets = await exchange.fetch_markets()
    
    if not markets:
        console.print("[red]X Nenhum mercado encontrado[/red]\n")
        return
    
    console.print(f"\n[green]OK {len(markets)} mercados encontrados![/green]\n")
    
    # Mostra primeiros mercados
    table = Table(title="Primeiros Mercados PredictIt")
    table.add_column("Pergunta", style="white", no_wrap=False, max_width=50)
    table.add_column("Preco", style="yellow")
    table.add_column("Volume", style="green")
    table.add_column("Liquidez", style="magenta")
    
    for market in markets[:15]:
        table.add_row(
            market.question[:47] + "..." if len(market.question) > 50 else market.question,
            f"${market.price:.3f}",
            f"${market.volume_24h:.0f}",
            f"${market.liquidity:.0f}"
        )
    
    console.print(table)
    
    # Estatisticas
    avg_price = sum(m.price for m in markets) / len(markets)
    total_volume = sum(m.volume_24h for m in markets)
    
    console.print(f"\n[cyan]Estatisticas:[/cyan]")
    console.print(f"  - Total de mercados: {len(markets)}")
    console.print(f"  - Preco medio: ${avg_price:.3f}")
    console.print(f"  - Volume total estimado: ${total_volume:,.0f}\n")
    
    console.print("[green]OK Integracao PredictIt funcionando![/green]\n")


if __name__ == "__main__":
    asyncio.run(test_predictit())
