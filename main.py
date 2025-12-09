"""CLI principal do sistema de arbitragem"""
import asyncio
import argparse
from monitor import ArbitrageMonitor
from rich.console import Console

console = Console()


async def analyze_once():
    """Executa análise única"""
    monitor = ArbitrageMonitor()
    await monitor.update()
    
    dashboard = monitor.render_dashboard()
    console.print(dashboard)
    
    if monitor.opportunities:
        console.print(f"\n[green]Encontradas {len(monitor.opportunities)} oportunidades![/green]")
        for i, opp in enumerate(monitor.opportunities[:5], 1):
            console.print(f"\n[bold]#{i}[/bold]")
            console.print(opp)
    else:
        console.print("[yellow]Nenhuma oportunidade encontrada no momento.[/yellow]")


async def monitor_continuous():
    """Executa monitor contínuo"""
    monitor = ArbitrageMonitor()
    await monitor.run()


async def search_event(query: str):
    """Busca eventos específicos"""
    monitor = ArbitrageMonitor()
    markets = await monitor.fetch_all_markets()
    
    # Filtra por query
    matching = [m for m in markets if query.lower() in m.question.lower()]
    
    console.print(f"[green]Encontrados {len(matching)} mercados relacionados a '{query}':[/green]\n")
    
    for market in matching[:10]:
        console.print(f"[cyan]{market.exchange}[/cyan] - {market.question}")
        console.print(f"  Preço: ${market.price:.4f} | Liquidez: ${market.liquidity:.0f}\n")


def main():
    parser = argparse.ArgumentParser(description="Prediction Market Arbitrage Bot")
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Monitoramento contínuo"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Análise única"
    )
    parser.add_argument(
        "--search",
        type=str,
        help="Buscar eventos específicos"
    )
    
    args = parser.parse_args()
    
    if args.monitor:
        asyncio.run(monitor_continuous())
    elif args.search:
        asyncio.run(search_event(args.search))
    else:
        # Padrão: análise única
        asyncio.run(analyze_once())


if __name__ == "__main__":
    main()

