"""Teste do modo de simulação - sem executar trades reais"""
import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from monitor import ArbitrageMonitor
from arbitrage import ArbitrageEngine
from market_normalizer import MarketNormalizer
from liquidity_filter import LiquidityFilter, LiquidityRequirements
from simulation_mode import SimulationEngine

console = Console()


async def test_simulation():
    """Testa modo de simulação completo"""
    
    console.print("\n[bold cyan]🧪 MODO SIMULAÇÃO - Teste Completo[/bold cyan]\n")
    console.print("[yellow]Testando sistema sem executar trades reais...[/yellow]\n")
    
    # 1. Busca mercados
    console.print("[cyan]1. Buscando mercados...[/cyan]")
    monitor = ArbitrageMonitor()
    markets = await monitor.fetch_all_markets()
    console.print(f"   ✓ {len(markets)} mercados encontrados\n")
    
    # 2. Aplica filtro de liquidez
    console.print("[cyan]2. Aplicando filtro de liquidez...[/cyan]")
    requirements = LiquidityRequirements(
        min_liquidity=50.0,
        min_volume_24h=20.0,
        max_spread_pct=0.10
    )
    liquidity_filter = LiquidityFilter(requirements)
    filtered_markets, filter_stats = liquidity_filter.filter_markets(markets)
    
    console.print(f"   ✓ {filter_stats['passed']}/{filter_stats['total']} mercados passaram no filtro")
    if filter_stats['reasons']:
        console.print("   Motivos de rejeição:")
        for reason, count in filter_stats['reasons'].items():
            console.print(f"     • {reason}: {count}x")
    console.print()
    
    # 3. Normaliza e encontra pares equivalentes
    console.print("[cyan]3. Encontrando mercados equivalentes...[/cyan]")
    normalizer = MarketNormalizer(
        min_text_similarity=0.50,
        max_date_difference_days=1
    )
    equivalent_pairs = normalizer.find_equivalent_pairs(filtered_markets)
    console.print(f"   ✓ {len(equivalent_pairs)} pares equivalentes encontrados\n")
    
    # 4. Calcula oportunidades de arbitragem
    console.print("[cyan]4. Calculando oportunidades de arbitragem...[/cyan]")
    engine = ArbitrageEngine()
    opportunities = []
    
    for m1, m2, validation in equivalent_pairs:
        opp = engine.calculate_arbitrage(m1, m2, confidence=validation['confidence'])
        if opp:
            opportunities.append(opp)
    
    console.print(f"   ✓ {len(opportunities)} oportunidades encontradas\n")
    
    if not opportunities:
        console.print("[yellow]⚠️  Nenhuma oportunidade encontrada no momento.[/yellow]")
        console.print("[dim]Isso é normal - oportunidades são raras.[/dim]\n")
        return
    
    # 5. Modo simulação
    console.print("[bold green]5. MODO SIMULAÇÃO - Testando oportunidades[/bold green]\n")
    
    sim_engine = SimulationEngine(initial_balance=10000.0)
    
    # Simula as melhores oportunidades
    best_opps = sorted(opportunities, key=lambda x: x.profit_pct, reverse=True)[:5]
    
    results_table = Table(title="🧪 Resultados da Simulação")
    results_table.add_column("ID", style="cyan")
    results_table.add_column("Compra", style="green")
    results_table.add_column("Venda", style="yellow")
    results_table.add_column("Valor", style="white")
    results_table.add_column("Lucro $", style="green bold")
    results_table.add_column("Lucro %", style="green bold")
    results_table.add_column("Status", style="white")
    
    for opp in best_opps:
        trade = sim_engine.simulate_trade(
            opp,
            amount_usd=500.0,
            include_slippage=True,
            slippage_pct=0.01
        )
        
        results_table.add_row(
            trade.id,
            f"{opp.market_buy.exchange}\n${trade.buy_price:.3f}",
            f"{opp.market_sell.exchange}\n${trade.sell_price:.3f}",
            f"${trade.amount_usd:.2f}",
            f"${trade.net_profit:.2f}",
            f"{trade.profit_pct:.2%}",
            "✅ Executado"
        )
    
    console.print(results_table)
    
    # 6. Estatísticas finais
    console.print()
    stats = sim_engine.get_statistics()
    
    stats_panel = Panel(
        f"""[bold]Estatísticas da Simulação[/bold]

💰 Balance Inicial: ${stats['initial_balance']:.2f}
💰 Balance Final: ${stats['current_balance']:.2f}
📊 ROI: [bold green]{stats['roi']:.2%}[/bold green]

📈 Total de Trades: {stats['total_trades']}
✅ Trades Lucrativos: {stats['winning_trades']}
❌ Trades Não Lucrativos: {stats['losing_trades']}
📊 Taxa de Acerto: {stats['win_rate']:.1%}

💵 Total Investido: ${stats['total_invested']:.2f}
💰 Lucro Total: ${stats['total_profit']:.2f}
📊 Lucro Médio: ${stats['avg_profit']:.2f} ({stats['avg_profit_pct']:.2%})
""",
        title="📊 Resumo",
        border_style="green"
    )
    
    console.print(stats_panel)
    
    # 7. Exporta relatório
    console.print("\n[cyan]Exportando relatório...[/cyan]")
    filename = sim_engine.export_report()
    console.print(f"[green]✓ Relatório salvo em: {filename}[/green]\n")
    
    console.print("[bold green]✅ Simulação concluída com sucesso![/bold green]")
    console.print("[dim]Nenhum trade real foi executado. Apenas simulação.[/dim]\n")


if __name__ == "__main__":
    asyncio.run(test_simulation())

