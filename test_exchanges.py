"""Testa todas as exchanges"""
import asyncio
from monitor import ArbitrageMonitor
from rich.console import Console

console = Console()

async def test():
    monitor = ArbitrageMonitor()
    
    console.print("\n[bold cyan]Testando todas as exchanges...[/bold cyan]\n")
    
    for exchange in monitor.exchanges:
        console.print(f"[yellow]Testando {exchange.name}...[/yellow]")
        try:
            markets = await exchange.fetch_markets()
            console.print(f"[green]✓ {exchange.name}: {len(markets)} mercados encontrados[/green]")
            if markets:
                console.print(f"   Exemplo: {markets[0].question[:50]}...")
        except Exception as e:
            console.print(f"[red]✗ {exchange.name}: ERRO - {e}[/red]")
    
    console.print("\n[bold cyan]Buscando todos os mercados...[/bold cyan]\n")
    all_markets = await monitor.fetch_all_markets()
    
    console.print(f"[green]Total de mercados: {len(all_markets)}[/green]")
    
    # Agrupa por exchange
    by_exchange = {}
    for market in all_markets:
        if market.exchange not in by_exchange:
            by_exchange[market.exchange] = 0
        by_exchange[market.exchange] += 1
    
    console.print("\n[bold]Mercados por exchange:[/bold]")
    for exchange, count in by_exchange.items():
        console.print(f"  {exchange}: {count} mercados")
    
    console.print("\n[bold cyan]Testando detecção de oportunidades...[/bold cyan]\n")
    await monitor.update()
    
    console.print(f"[green]Oportunidades encontradas: {len(monitor.opportunities)}[/green]")
    
    if monitor.opportunities:
        console.print("\n[bold]Top 3 oportunidades:[/bold]")
        for i, opp in enumerate(monitor.opportunities[:3], 1):
            console.print(f"\n  {i}. Lucro: {opp.profit_pct:.2%}")
            console.print(f"     Comprar: {opp.market_buy.exchange} @ ${opp.buy_price:.4f}")
            console.print(f"     Vender: {opp.market_sell.exchange} @ ${opp.sell_price:.4f}")
    else:
        console.print("[yellow]Nenhuma oportunidade encontrada. Possíveis razões:[/yellow]")
        console.print("  - Não há mercados similares entre exchanges")
        console.print("  - Diferenças de preço não são suficientes para arbitragem")
        console.print("  - Liquidez insuficiente")

if __name__ == "__main__":
    asyncio.run(test())

