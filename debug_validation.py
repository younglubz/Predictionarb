"""Debug para entender por que não passam na validação"""
import asyncio
from monitor import ArbitrageMonitor
from arbitrage import ArbitrageEngine
from market_validator import MarketValidator
from rich.console import Console

console = Console()

async def debug():
    monitor = ArbitrageMonitor()
    markets = await monitor.fetch_all_markets()
    matches = monitor.matcher.find_matching_events(markets)
    
    console.print(f"\n[cyan]Analisando {len(matches)} pares...[/cyan]\n")
    
    validator = MarketValidator()
    engine = ArbitrageEngine()
    
    blocked_reasons = {}
    
    for m1, m2 in matches[:20]:  # Analisa primeiros 20
        # Tenta validação
        equivalent, validation = validator.validate_equivalence(m1, m2, min_similarity=0.35)
        
        if not equivalent:
            reason = ", ".join(validation["issues"])
            blocked_reasons[reason] = blocked_reasons.get(reason, 0) + 1
            
            console.print(f"[red]❌ Bloqueado:[/red]")
            console.print(f"  M1: {m1.question[:50]}...")
            console.print(f"  M2: {m2.question[:50]}...")
            console.print(f"  Razão: {reason}")
            console.print(f"  Preços: ${m1.price:.3f} vs ${m2.price:.3f}")
            console.print(f"  Liquidez: ${m1.liquidity:.0f} vs ${m2.liquidity:.0f}\n")
    
    console.print("\n[cyan]Resumo de razões de bloqueio:[/cyan]")
    for reason, count in sorted(blocked_reasons.items(), key=lambda x: x[1], reverse=True):
        console.print(f"  • {reason}: {count}x")

asyncio.run(debug())

