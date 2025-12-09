"""Script para encontrar oportunidades reais de arbitragem"""
import asyncio
from monitor import ArbitrageMonitor
from matcher import EventMatcher
from rich.console import Console
from rich.table import Table

console = Console()

async def find_opportunities():
    """Busca oportunidades reais com análise detalhada"""
    console.print("\n[bold cyan]🔍 Buscando oportunidades reais de arbitragem...[/bold cyan]\n")
    
    monitor = ArbitrageMonitor()
    
    # Busca mercados
    console.print("[yellow]Buscando mercados...[/yellow]")
    markets = await monitor.fetch_all_markets()
    
    # Agrupa por exchange
    by_exchange = {}
    for market in markets:
        if market.exchange not in by_exchange:
            by_exchange[market.exchange] = []
        by_exchange[market.exchange].append(market)
    
    console.print(f"\n[green]✓ Total de mercados: {len(markets)}[/green]")
    for exchange, mkts in by_exchange.items():
        console.print(f"  • {exchange}: {len(mkts)} mercados")
    
    # Encontra matches
    console.print("\n[yellow]Procurando eventos similares entre exchanges...[/yellow]")
    matches = monitor.matcher.find_matching_events(markets)
    console.print(f"[green]✓ Encontrados {len(matches)} pares similares[/green]\n")
    
    if not matches:
        console.print("[red]❌ Nenhum par similar encontrado![/red]")
        console.print("\n[yellow]Dica:[/yellow] As exchanges podem ter mercados sobre tópicos muito diferentes.")
        console.print("Vamos mostrar exemplos de mercados de cada exchange:\n")
        
        for exchange, mkts in by_exchange.items():
            console.print(f"[cyan]{exchange.upper()}:[/cyan]")
            for m in mkts[:5]:
                console.print(f"  • {m.question[:70]}... (${m.price:.3f})")
            console.print()
        return
    
    # Mostra top matches
    table = Table(title="Top 10 Pares Similares")
    table.add_column("Similaridade", style="cyan")
    table.add_column("Exchange 1", style="green")
    table.add_column("Exchange 2", style="green")
    table.add_column("Pergunta 1", style="white")
    table.add_column("Pergunta 2", style="white")
    table.add_column("Preços", style="yellow")
    
    for m1, m2 in matches[:10]:
        similarity = monitor.matcher.calculate_similarity(m1.question, m2.question)
        table.add_row(
            f"{similarity:.1%}",
            m1.exchange,
            m2.exchange,
            m1.question[:40] + "...",
            m2.question[:40] + "...",
            f"${m1.price:.3f} vs ${m2.price:.3f}"
        )
    
    console.print(table)
    
    # Calcula arbitragem
    console.print("\n[yellow]Calculando oportunidades de arbitragem...[/yellow]")
    opportunities = []
    from arbitrage import ArbitrageEngine
    engine = ArbitrageEngine()
    for m1, m2 in matches:
        opp = engine.calculate_arbitrage(m1, m2)
        if opp:
            opportunities.append(opp)
    
    console.print(f"[green]✓ Encontradas {len(opportunities)} oportunidades![/green]\n")
    
    if not opportunities:
        console.print("[yellow]⚠️ Nenhuma oportunidade com lucro suficiente encontrada.[/yellow]")
        console.print(f"Possíveis razões:")
        console.print(f"  • Diferença de preços < 1% (após taxas)")
        console.print(f"  • Liquidez < $50")
        console.print(f"  • Mercados não equivalentes\n")
        return
    
    # Mostra oportunidades
    opp_table = Table(title=f"🚀 {len(opportunities)} Oportunidades de Arbitragem Encontradas!")
    opp_table.add_column("Lucro %", style="green bold")
    opp_table.add_column("Lucro $", style="green")
    opp_table.add_column("Comprar em", style="cyan")
    opp_table.add_column("Vender em", style="yellow")
    opp_table.add_column("Preços", style="white")
    opp_table.add_column("Confiança", style="magenta")
    
    for opp in sorted(opportunities, key=lambda x: x.profit_pct, reverse=True)[:20]:
        opp_table.add_row(
            f"{opp.profit_pct:.2%}",
            f"${opp.net_profit:.2f}",
            f"{opp.market_buy.exchange}\n{opp.market_buy.question[:35]}...",
            f"{opp.market_sell.exchange}\n{opp.market_sell.question[:35]}...",
            f"${opp.buy_price:.3f} → ${opp.sell_price:.3f}",
            f"{opp.confidence:.0%}"
        )
    
    console.print(opp_table)
    console.print(f"\n[green]✅ Total de {len(opportunities)} oportunidades disponíveis![/green]\n")

if __name__ == "__main__":
    asyncio.run(find_opportunities())

