"""Testa matching entre Polymarket e Manifold"""
import asyncio
from monitor import ArbitrageMonitor
from rich.console import Console

console = Console()

async def test():
    monitor = ArbitrageMonitor()
    
    console.print("\n[bold cyan]Buscando mercados...[/bold cyan]\n")
    all_markets = await monitor.fetch_all_markets()
    
    console.print(f"[green]Total: {len(all_markets)} mercados[/green]")
    
    # Agrupa por exchange
    by_exchange = {}
    for market in all_markets:
        if market.exchange not in by_exchange:
            by_exchange[market.exchange] = []
        by_exchange[market.exchange].append(market)
    
    console.print("\n[bold]Mercados por exchange:[/bold]")
    for exchange, markets in by_exchange.items():
        console.print(f"  {exchange}: {len(markets)} mercados")
    
    # Testa matching
    console.print("\n[bold cyan]Testando matching...[/bold cyan]\n")
    matches = monitor.matcher.find_matching_events(all_markets)
    
    console.print(f"[green]Pares similares encontrados: {len(matches)}[/green]\n")
    
    if matches:
        console.print("[bold]Exemplos de matches:[/bold]")
        for i, (m1, m2) in enumerate(matches[:5], 1):
            console.print(f"\n  {i}. {m1.exchange} vs {m2.exchange}")
            console.print(f"     Q1: {m1.question[:60]}...")
            console.print(f"     Q2: {m2.question[:60]}...")
            console.print(f"     Similaridade: {monitor.matcher.calculate_similarity(m1.question, m2.question):.2%}")
            console.print(f"     Preços: ${m1.price:.4f} vs ${m2.price:.4f}")
    else:
        console.print("[yellow]Nenhum match encontrado. Possíveis razões:[/yellow]")
        console.print("  - Perguntas muito diferentes entre exchanges")
        console.print("  - Threshold de similaridade muito alto")
        console.print("  - Tópicos diferentes em cada exchange")
        
        # Mostra exemplos de perguntas
        console.print("\n[bold]Exemplos de perguntas Polymarket:[/bold]")
        for m in list(by_exchange.get("polymarket", []))[:3]:
            console.print(f"  - {m.question[:70]}...")
        
        console.print("\n[bold]Exemplos de perguntas Manifold:[/bold]")
        for m in list(by_exchange.get("manifold", []))[:3]:
            console.print(f"  - {m.question[:70]}...")

if __name__ == "__main__":
    asyncio.run(test())

