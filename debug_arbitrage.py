"""Debug para entender por que não geram oportunidades"""
import asyncio
from monitor import ArbitrageMonitor
from arbitrage import ArbitrageEngine
from rich.console import Console
from rich.table import Table

console = Console()

async def debug():
    monitor = ArbitrageMonitor()
    markets = await monitor.fetch_all_markets()
    matches = monitor.matcher.find_matching_events(markets)
    
    console.print(f"\n[cyan]Analisando {len(matches)} pares para arbitragem...[/cyan]\n")
    
    engine = ArbitrageEngine()
    
    table = Table(title="Análise de Oportunidades")
    table.add_column("Mercados", style="white")
    table.add_column("Preços", style="cyan")
    table.add_column("Diferença", style="yellow")
    table.add_column("Lucro Bruto", style="green")
    table.add_column("Taxas", style="red")
    table.add_column("Lucro Líquido", style="magenta")
    table.add_column("Status", style="white")
    
    for m1, m2 in matches[:15]:
        # Calcula manualmente
        price_diff = abs(m1.price - m2.price)
        
        # Simula compra no mais barato, venda no mais caro
        if m1.price < m2.price:
            buy_market, sell_market = m1, m2
        else:
            buy_market, sell_market = m2, m1
        
        buy_price = buy_market.price
        sell_price = sell_market.price
        
        # Calcula lucro bruto
        profit_gross = sell_price - buy_price
        
        # Taxas
        from config import EXCHANGE_FEES
        fee_buy = EXCHANGE_FEES.get(buy_market.exchange, 0.02)
        fee_sell = EXCHANGE_FEES.get(sell_market.exchange, 0.02)
        total_fees = fee_buy + fee_sell
        
        # Lucro líquido
        profit_net = profit_gross - total_fees
        profit_pct = (profit_net / buy_price) * 100 if buy_price > 0 else 0
        
        # Tenta calcular via engine
        opp = engine.calculate_arbitrage(m1, m2)
        
        status = "✅ Oportunidade!" if opp else "❌ Bloqueado"
        
        table.add_row(
            f"{buy_market.exchange} → {sell_market.exchange}\n{m1.question[:30]}...",
            f"${buy_price:.3f} → ${sell_price:.3f}",
            f"${price_diff:.3f}",
            f"${profit_gross:.3f} ({profit_gross*100:.1f}%)",
            f"${total_fees:.3f} ({total_fees*100:.1f}%)",
            f"${profit_net:.3f} ({profit_pct:.1f}%)",
            status
        )
    
    console.print(table)
    
    console.print(f"\n[yellow]Configuração atual:[/yellow]")
    console.print(f"  MIN_ARBITRAGE_PROFIT: 1%")
    console.print(f"  MIN_LIQUIDITY: $50")
    console.print(f"  Taxas Polymarket: 2%")
    console.print(f"  Taxas Manifold: 0%")

asyncio.run(debug())

