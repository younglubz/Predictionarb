"""Teste da integração Kalshi v2"""
import asyncio
from exchanges.kalshi_v2 import KalshiV2Exchange
from rich.console import Console
from rich.table import Table

console = Console()


async def test_kalshi():
    console.print("\n[bold cyan]Testando Kalshi API v2[/bold cyan]\n")
    console.print("[yellow]Documentacao: https://docs.kalshi.com/[/yellow]\n")
    
    exchange = KalshiV2Exchange()
    
    console.print(f"[cyan]API URL:[/cyan] {exchange.api_url}")
    console.print(f"[cyan]Modo:[/cyan] {'Demo' if exchange.use_demo else 'Produção'}\n")
    
    # Busca mercados
    console.print("[yellow]Buscando mercados...[/yellow]")
    markets = await exchange.fetch_markets()
    
    if not markets:
        console.print("[red]X Nenhum mercado encontrado[/red]")
        console.print("\n[yellow]Possiveis causas:[/yellow]")
        console.print("  - API pode estar temporariamente indisponivel")
        console.print("  - Pode precisar de API key para alguns endpoints")
        console.print("  - Verificar se demo API esta ativa\n")
        return
    
    console.print(f"\n[green]OK {len(markets)} mercados encontrados![/green]\n")
    
    # Mostra primeiros mercados
    table = Table(title="Primeiros Mercados Kalshi")
    table.add_column("Pergunta", style="white", no_wrap=False, max_width=50)
    table.add_column("Outcome", style="cyan")
    table.add_column("Preço", style="yellow")
    table.add_column("Volume", style="green")
    table.add_column("Liquidez", style="magenta")
    
    for market in markets[:10]:
        table.add_row(
            market.question[:47] + "..." if len(market.question) > 50 else market.question,
            market.outcome,
            f"${market.price:.3f}",
            f"${market.volume_24h:.0f}",
            f"${market.liquidity:.0f}"
        )
    
    console.print(table)
    
    # Estatísticas
    yes_markets = [m for m in markets if m.outcome == "YES"]
    no_markets = [m for m in markets if m.outcome == "NO"]
    avg_price = sum(m.price for m in markets) / len(markets)
    total_volume = sum(m.volume_24h for m in markets)
    
    console.print(f"\n[cyan]Estatísticas:[/cyan]")
    console.print(f"  • Total de mercados: {len(markets)}")
    console.print(f"  • YES markets: {len(yes_markets)}")
    console.print(f"  • NO markets: {len(no_markets)}")
    console.print(f"  • Preço médio: ${avg_price:.3f}")
    console.print(f"  • Volume total: ${total_volume:,.0f}\n")
    
    console.print("[green]OK Integracao Kalshi funcionando![/green]\n")


if __name__ == "__main__":
    asyncio.run(test_kalshi())

