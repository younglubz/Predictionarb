"""
Script de diagnóstico para entender por que não há oportunidades de arbitragem.
"""
import asyncio
from monitor import ArbitrageMonitor
from config import MIN_ARBITRAGE_PROFIT, MIN_LIQUIDITY
from rich.console import Console
from rich.table import Table

console = Console()

async def diagnose():
    console.print("\n[cyan]═══════════════════════════════════════════════════════════[/cyan]")
    console.print("[cyan]       DIAGNÓSTICO DE OPORTUNIDADES DE ARBITRAGEM[/cyan]")
    console.print("[cyan]═══════════════════════════════════════════════════════════[/cyan]\n")
    
    # Criar monitor
    monitor = ArbitrageMonitor()
    
    console.print("[yellow]📊 Configurações Atuais:[/yellow]")
    console.print(f"   • MIN_ARBITRAGE_PROFIT: {MIN_ARBITRAGE_PROFIT * 100:.2f}%")
    console.print(f"   • MIN_LIQUIDITY: ${MIN_LIQUIDITY}")
    console.print(f"   • Similarity Threshold: {monitor.matcher.similarity_threshold * 100:.0f}%")
    console.print(f"   • Max Date Diff: {monitor.matcher.max_date_diff_days} dias\n")
    
    # Buscar mercados
    console.print("[yellow]🔍 Buscando mercados...[/yellow]")
    await monitor.update()
    
    console.print(f"[green]✓ {len(monitor._cached_markets)} mercados encontrados[/green]\n")
    
    # Verificar matches
    console.print(f"[yellow]🔗 Matches encontrados: {len(monitor.matches)}[/yellow]")
    
    if not monitor.matches:
        console.print("[red]❌ Nenhum match encontrado![/red]")
        console.print("[yellow]Sugestão: Reduza o similarity_threshold[/yellow]\n")
        return
    
    # Analisar cada match
    console.print(f"\n[cyan]📋 Analisando {len(monitor.matches)} matches...[/cyan]\n")
    
    stats = {
        "total_matches": len(monitor.matches),
        "sem_preco": 0,
        "preco_invalido": 0,
        "sem_liquidez": 0,
        "lucro_insuficiente": 0,
        "validacao_falhou": 0,
        "oportunidades_validas": 0
    }
    
    valid_opportunities = []
    
    for i, (m1, m2, similarity) in enumerate(monitor.matches[:20], 1):  # Analisa primeiros 20
        console.print(f"[cyan]Match {i}:[/cyan] {similarity:.1f}% similaridade")
        console.print(f"  Market 1: [{m1.exchange}] {m1.question[:60]}...")
        console.print(f"  Market 2: [{m2.exchange}] {m2.question[:60]}...")
        
        # Verificar preços
        if m1.yes_price is None or m2.no_price is None:
            console.print(f"  [red]✗ Preços ausentes[/red] (M1 Yes: {m1.yes_price}, M2 No: {m2.no_price})")
            stats["sem_preco"] += 1
            continue
        
        if m1.yes_price <= 0 or m1.yes_price >= 1 or m2.no_price <= 0 or m2.no_price >= 1:
            console.print(f"  [red]✗ Preços inválidos[/red] (M1 Yes: {m1.yes_price:.3f}, M2 No: {m2.no_price:.3f})")
            stats["preco_invalido"] += 1
            continue
        
        # Calcular lucro potencial
        total_cost = m1.yes_price + m2.no_price
        if total_cost >= 1:
            console.print(f"  [red]✗ Sem lucro[/red] (Custo: ${total_cost:.3f})")
            stats["lucro_insuficiente"] += 1
            continue
        
        profit = 1 - total_cost
        profit_pct = profit / total_cost if total_cost > 0 else 0
        
        # Verificar liquidez
        min_liquidity = min(m1.volume or 0, m2.volume or 0)
        if min_liquidity < MIN_LIQUIDITY:
            console.print(f"  [yellow]⚠ Liquidez baixa[/yellow] (${min_liquidity:.0f} < ${MIN_LIQUIDITY})")
            stats["sem_liquidez"] += 1
            continue
        
        # Verificar lucro mínimo
        if profit_pct < MIN_ARBITRAGE_PROFIT:
            console.print(f"  [yellow]⚠ Lucro insuficiente[/yellow] ({profit_pct*100:.2f}% < {MIN_ARBITRAGE_PROFIT*100:.2f}%)")
            stats["lucro_insuficiente"] += 1
            continue
        
        # Oportunidade válida!
        console.print(f"  [green]✓ OPORTUNIDADE VÁLIDA![/green]")
        console.print(f"    Lucro: {profit_pct*100:.2f}% | Liquidez: ${min_liquidity:.0f}")
        stats["oportunidades_validas"] += 1
        valid_opportunities.append((m1, m2, profit_pct, min_liquidity))
        console.print()
    
    # Resumo
    console.print("\n[cyan]═══════════════════════════════════════════════════════════[/cyan]")
    console.print("[cyan]                        RESUMO[/cyan]")
    console.print("[cyan]═══════════════════════════════════════════════════════════[/cyan]\n")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Motivo")
    table.add_column("Quantidade", justify="right")
    table.add_column("%", justify="right")
    
    total = stats["total_matches"]
    table.add_row("Total de Matches", str(total), "100%")
    table.add_row("Sem Preços", str(stats["sem_preco"]), f"{stats['sem_preco']/total*100:.1f}%")
    table.add_row("Preços Inválidos", str(stats["preco_invalido"]), f"{stats['preco_invalido']/total*100:.1f}%")
    table.add_row("Sem Liquidez", str(stats["sem_liquidez"]), f"{stats['sem_liquidez']/total*100:.1f}%")
    table.add_row("Lucro Insuficiente", str(stats["lucro_insuficiente"]), f"{stats['lucro_insuficiente']/total*100:.1f}%")
    table.add_row("[green]Oportunidades Válidas[/green]", f"[green]{stats['oportunidades_validas']}[/green]", f"[green]{stats['oportunidades_validas']/total*100:.1f}%[/green]")
    
    console.print(table)
    
    # Recomendações
    console.print("\n[yellow]💡 RECOMENDAÇÕES:[/yellow]\n")
    
    if stats["oportunidades_validas"] == 0:
        if stats["lucro_insuficiente"] > total * 0.3:
            console.print(f"   • Muitos matches rejeitados por lucro insuficiente ({stats['lucro_insuficiente']})")
            console.print(f"   • Considere reduzir MIN_ARBITRAGE_PROFIT de {MIN_ARBITRAGE_PROFIT*100:.1f}% para 1%")
        
        if stats["sem_liquidez"] > total * 0.3:
            console.print(f"   • Muitos matches rejeitados por falta de liquidez ({stats['sem_liquidez']})")
            console.print(f"   • Considere reduzir MIN_LIQUIDITY de ${MIN_LIQUIDITY} para $50")
        
        if stats["sem_preco"] > total * 0.3:
            console.print(f"   • Muitos mercados sem preços ({stats['sem_preco']})")
            console.print(f"   • Problema nas APIs das exchanges")
        
        console.print("\n   [red]⚠ IMPORTANTE: Oportunidades de arbitragem são RARAS![/red]")
        console.print("   Mercados eficientes corrigem discrepâncias rapidamente.")
    else:
        console.print(f"   [green]✓ {stats['oportunidades_validas']} oportunidades válidas encontradas![/green]")
        console.print("   Verifique se o endpoint /opportunities as está retornando.")
    
    console.print("\n[cyan]═══════════════════════════════════════════════════════════[/cyan]\n")

if __name__ == "__main__":
    asyncio.run(diagnose())

