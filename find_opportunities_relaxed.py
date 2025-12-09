# -*- coding: utf-8 -*-
"""Busca oportunidades com filtros MUITO RELAXADOS"""
import asyncio
from monitor import ArbitrageMonitor
from matcher import EventMatcher
from rich.console import Console
from rich.table import Table
from datetime import datetime, timezone

console = Console()


async def find_opportunities_relaxed():
    console.print("\n[bold cyan]Buscando Oportunidades com Filtros Relaxados[/bold cyan]\n")
    
    # Inicializa com thresholds baixos
    monitor = ArbitrageMonitor()
    matcher = EventMatcher(similarity_threshold=0.30)  # 30% apenas!
    
    # Busca mercados
    console.print("[yellow]1. Buscando mercados...[/yellow]")
    all_markets = []
    
    for exchange in monitor.exchanges:
        try:
            markets = await exchange.fetch_markets()
            all_markets.extend(markets)
            console.print(f"   {exchange.name}: {len(markets)} mercados")
        except Exception as e:
            console.print(f"   [red]{exchange.name}: erro[/red]")
    
    console.print(f"\n   Total: {len(all_markets)} mercados\n")
    
    # Filtragem MINIMA
    console.print("[yellow]2. Filtragem minima...[/yellow]")
    viable_markets = []
    
    for market in all_markets:
        # Criterios MUITO relaxados
        if (market.price > 0.001 and market.price < 0.999 and  # Quase qualquer preco
            market.liquidity > 1):  # Liquidez minima ridicula
            viable_markets.append(market)
    
    console.print(f"   {len(viable_markets)} mercados viaveis\n")
    
    # Busca pares com similaridade MUITO baixa
    console.print("[yellow]3. Buscando pares similares (threshold 30%)...[/yellow]")
    
    similar_pairs = []
    checked = set()
    
    for i, m1 in enumerate(viable_markets):
        for m2 in viable_markets[i+1:]:
            if m1.exchange == m2.exchange:
                continue
            
            pair_key = tuple(sorted([m1.market_id, m2.market_id]))
            if pair_key in checked:
                continue
            checked.add(pair_key)
            
            # Similaridade >= 30%
            sim = matcher.calculate_similarity(m1.question, m2.question)
            if sim < 0.30:
                continue
            
            # Outcomes devem ser compativeis
            if not (m1.outcome == m2.outcome or 
                    (m1.outcome == "YES" and m2.outcome == "NO") or
                    (m1.outcome == "NO" and m2.outcome == "YES")):
                continue
            
            # Calcula diferenca de preco
            if m1.outcome == m2.outcome:
                price_diff = abs(m1.price - m2.price)
            else:
                if m1.outcome == "YES":
                    price_diff = abs(m1.price - (1 - m2.price))
                else:
                    price_diff = abs((1 - m1.price) - m2.price)
            
            # QUALQUER diferenca > 0.1% ja conta!
            if price_diff > 0.001:
                similar_pairs.append({
                    'market1': m1,
                    'market2': m2,
                    'similarity': sim,
                    'price_diff': price_diff,
                    'potential_profit': price_diff * 0.8  # Estimativa apos taxas
                })
    
    console.print(f"   {len(similar_pairs)} pares encontrados\n")
    
    if not similar_pairs:
        console.print("[yellow]Nenhum par encontrado mesmo com filtros relaxados![/yellow]\n")
        return
    
    # Ordena por diferenca de preco
    similar_pairs.sort(key=lambda x: x['price_diff'], reverse=True)
    
    # Mostra top 30
    console.print("[bold green]Top 30 Oportunidades Potenciais:[/bold green]\n")
    
    table = Table(title="Oportunidades com Filtros Relaxados")
    table.add_column("#", style="cyan", width=3)
    table.add_column("Similaridade", style="yellow", width=12)
    table.add_column("Exchange A", style="cyan", width=12)
    table.add_column("Preco A", style="green", width=9)
    table.add_column("Exchange B", style="magenta", width=12)
    table.add_column("Preco B", style="green", width=9)
    table.add_column("Diff", style="yellow", width=7)
    table.add_column("Lucro Est.", style="green", width=10)
    
    for i, pair in enumerate(similar_pairs[:30], 1):
        m1 = pair['market1']
        m2 = pair['market2']
        
        table.add_row(
            str(i),
            f"{pair['similarity']*100:.0f}%",
            m1.exchange[:10],
            f"${m1.price:.3f}",
            m2.exchange[:10],
            f"${m2.price:.3f}",
            f"{pair['price_diff']*100:.1f}%",
            f"${pair['potential_profit']:.3f}"
        )
    
    console.print(table)
    
    # Estatisticas
    console.print(f"\n[cyan]Estatisticas:[/cyan]")
    console.print(f"  - Total de mercados: {len(all_markets)}")
    console.print(f"  - Mercados viaveis: {len(viable_markets)} ({len(viable_markets)/len(all_markets)*100:.1f}%)")
    console.print(f"  - Pares similares: {len(similar_pairs)}")
    console.print(f"  - Melhor diferenca: {similar_pairs[0]['price_diff']*100:.1f}%")
    
    avg_similarity = sum(p['similarity'] for p in similar_pairs) / len(similar_pairs)
    console.print(f"  - Similaridade media: {avg_similarity*100:.1f}%")
    
    # Top 5 detalhados
    console.print(f"\n[bold yellow]Top 5 Detalhados:[/bold yellow]\n")
    
    for i, pair in enumerate(similar_pairs[:5], 1):
        m1 = pair['market1']
        m2 = pair['market2']
        
        console.print(f"[bold]#{i}[/bold]")
        console.print(f"  Similaridade: {pair['similarity']*100:.0f}%")
        console.print(f"  ")
        console.print(f"  [cyan]{m1.exchange}:[/cyan]")
        console.print(f"    {m1.question[:70]}...")
        console.print(f"    Outcome: {m1.outcome}, Preco: ${m1.price:.3f}, Liquidez: ${m1.liquidity:.0f}")
        console.print(f"  ")
        console.print(f"  [magenta]{m2.exchange}:[/magenta]")
        console.print(f"    {m2.question[:70]}...")
        console.print(f"    Outcome: {m2.outcome}, Preco: ${m2.price:.3f}, Liquidez: ${m2.liquidity:.0f}")
        console.print(f"  ")
        console.print(f"  [yellow]Diferenca:[/yellow] {pair['price_diff']*100:.1f}%")
        console.print(f"  [green]Lucro Estimado:[/green] ${pair['potential_profit']:.3f}")
        console.print()


if __name__ == "__main__":
    asyncio.run(find_opportunities_relaxed())

