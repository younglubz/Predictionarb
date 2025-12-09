"""Monitor diário automático de oportunidades de arbitragem"""
import asyncio
import schedule
import time
from datetime import datetime
from monitor import ArbitrageMonitor
from arbitrage import ArbitrageEngine
from rich.console import Console
from rich.table import Table
import json
import os

console = Console()


async def check_opportunities():
    """Verifica oportunidades e salva em log"""
    console.print(f"\n[cyan]{'='*60}[/cyan]")
    console.print(f"[bold green]🔍 Verificação Diária - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/bold green]")
    console.print(f"[cyan]{'='*60}[/cyan]\n")
    
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
    console.print("\n[yellow]Procurando eventos similares...[/yellow]")
    matches = monitor.matcher.find_matching_events(markets)
    console.print(f"[green]✓ Encontrados {len(matches)} pares similares[/green]")
    
    # Calcula arbitragem
    console.print("\n[yellow]Calculando oportunidades...[/yellow]")
    engine = ArbitrageEngine()
    opportunities = []
    
    for m1, m2 in matches:
        opp = engine.calculate_arbitrage(m1, m2)
        if opp:
            opportunities.append(opp)
    
    console.print(f"[bold green]✓ Encontradas {len(opportunities)} oportunidades![/bold green]\n")
    
    # Log detalhado
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "total_markets": len(markets),
        "by_exchange": {ex: len(mkts) for ex, mkts in by_exchange.items()},
        "similar_pairs": len(matches),
        "opportunities": len(opportunities),
        "details": []
    }
    
    if opportunities:
        # Mostra oportunidades
        table = Table(title=f"🚀 {len(opportunities)} Oportunidades Encontradas!")
        table.add_column("Lucro %", style="green bold")
        table.add_column("Lucro $", style="green")
        table.add_column("Comprar", style="cyan")
        table.add_column("Vender", style="yellow")
        table.add_column("Preços", style="white")
        
        for opp in sorted(opportunities, key=lambda x: x.profit_pct, reverse=True)[:10]:
            table.add_row(
                f"{opp.profit_pct:.2%}",
                f"${opp.net_profit:.2f}",
                f"{opp.market_buy.exchange}\n{opp.market_buy.question[:30]}...",
                f"{opp.market_sell.exchange}\n{opp.market_sell.question[:30]}...",
                f"${opp.buy_price:.3f} → ${opp.sell_price:.3f}"
            )
            
            # Adiciona ao log
            log_entry["details"].append({
                "profit_pct": opp.profit_pct,
                "profit_abs": opp.net_profit,
                "buy_exchange": opp.market_buy.exchange,
                "sell_exchange": opp.market_sell.exchange,
                "buy_price": opp.buy_price,
                "sell_price": opp.sell_price,
                "question": opp.market_buy.question
            })
        
        console.print(table)
        console.print(f"\n[bold green]💰 Melhor oportunidade: {opportunities[0].profit_pct:.2%} de lucro![/bold green]\n")
    else:
        console.print("[yellow]⚠️  Nenhuma oportunidade encontrada no momento.[/yellow]\n")
    
    # Salva log
    log_file = "arbitrage_log.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    console.print(f"[dim]Log salvo em: {log_file}[/dim]")
    console.print(f"[cyan]{'='*60}[/cyan]\n")
    
    return len(opportunities)


def run_daily_check():
    """Executa verificação diária"""
    asyncio.run(check_opportunities())


def start_scheduler():
    """Inicia scheduler para verificações automáticas"""
    console.print("\n[bold cyan]📅 Monitor Diário de Arbitragem Iniciado[/bold cyan]\n")
    console.print("[green]Horários de verificação:[/green]")
    console.print("  • 09:00 - Manhã")
    console.print("  • 15:00 - Tarde")
    console.print("  • 21:00 - Noite")
    console.print("\n[yellow]Aguardando próxima verificação...[/yellow]\n")
    
    # Agenda verificações
    schedule.every().day.at("09:00").do(run_daily_check)
    schedule.every().day.at("15:00").do(run_daily_check)
    schedule.every().day.at("21:00").do(run_daily_check)
    
    # Executa verificação imediata
    console.print("[cyan]Executando verificação inicial...[/cyan]")
    run_daily_check()
    
    # Loop
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verifica a cada minuto


if __name__ == "__main__":
    start_scheduler()

