# -*- coding: utf-8 -*-
"""Teste de todas as exchanges integradas"""
import asyncio
from exchanges.polymarket import PolymarketExchange
from exchanges.manifold import ManifoldExchange
from exchanges.predictit_v2 import PredictItV2Exchange
from exchanges.kalshi_v2 import KalshiV2Exchange
from rich.console import Console
from rich.table import Table

console = Console()


async def test_all():
    console.print("\n[bold cyan]Testando Todas as Exchanges[/bold cyan]\n")
    
    exchanges = [
        ("Polymarket", PolymarketExchange()),
        ("Manifold", ManifoldExchange()),
        ("PredictIt", PredictItV2Exchange()),
        ("Kalshi", KalshiV2Exchange()),
    ]
    
    table = Table(title="Status das Exchanges")
    table.add_column("Exchange", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Mercados", style="green")
    table.add_column("Observacoes", style="yellow")
    
    total_markets = 0
    
    for name, exchange in exchanges:
        console.print(f"[yellow]Testando {name}...[/yellow]")
        try:
            markets = await exchange.fetch_markets()
            market_count = len(markets)
            total_markets += market_count
            
            if market_count > 0:
                table.add_row(
                    name,
                    "[green]OK[/green]",
                    str(market_count),
                    "Funcionando"
                )
            else:
                table.add_row(
                    name,
                    "[yellow]WARN[/yellow]",
                    "0",
                    "API retornou 0 mercados"
                )
        except Exception as e:
            table.add_row(
                name,
                "[red]ERRO[/red]",
                "0",
                str(e)[:30]
            )
    
    console.print(table)
    
    console.print(f"\n[bold green]Total: {total_markets} mercados disponiveis[/bold green]")
    console.print("\n[cyan]Sistema pronto para arbitragem![/cyan]\n")


if __name__ == "__main__":
    asyncio.run(test_all())

