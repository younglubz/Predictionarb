# -*- coding: utf-8 -*-
"""Analise detalhada de mercados similares para arbitragem"""
import asyncio
from monitor import ArbitrageMonitor
from matcher import EventMatcher
from rich.console import Console
from rich.table import Table

console = Console()


async def find_similar_markets():
    console.print("\n[bold cyan]Analisando todos os mercados para encontrar pares similares[/bold cyan]\n")
    
    # Inicializa monitor
    monitor = ArbitrageMonitor()
    matcher = EventMatcher()
    
    # Busca mercados
    console.print("[yellow]1. Buscando mercados de todas as exchanges...[/yellow]")
    all_markets = []
    
    for exchange in monitor.exchanges:
        try:
            markets = await exchange.fetch_markets()
            all_markets.extend(markets)
            console.print(f"   {exchange.name}: {len(markets)} mercados")
        except Exception as e:
            console.print(f"   [red]Erro em {exchange.name}: {str(e)}[/red]")
    
    total_markets = len(all_markets)
    console.print(f"\n   OK {total_markets} mercados encontrados\n")
    
    # Agrupa por exchange
    by_exchange = {}
    for market in all_markets:
        if market.exchange not in by_exchange:
            by_exchange[market.exchange] = []
        by_exchange[market.exchange].append(market)
    
    console.print("[cyan]Mercados por exchange:[/cyan]")
    for exchange, markets in by_exchange.items():
        console.print(f"  - {exchange}: {len(markets)} mercados")
    
    # Encontra pares similares com threshold mais baixo
    console.print("\n[yellow]2. Buscando pares similares (threshold 50%)...[/yellow]")
    
    similar_pairs = []
    checked = set()
    
    for i, market1 in enumerate(all_markets):
        for market2 in all_markets[i+1:]:
            # Pula se mesma exchange
            if market1.exchange == market2.exchange:
                continue
            
            # Pula se ja checou
            pair_key = tuple(sorted([market1.market_id, market2.market_id]))
            if pair_key in checked:
                continue
            checked.add(pair_key)
            
            # Calcula similaridade
            similarity = matcher.calculate_similarity(
                market1.question,
                market2.question
            )
            
            # Se similaridade >= 50%
            if similarity >= 0.50:
                # Verifica se outcomes sao opostos ou iguais
                outcome_match = (
                    market1.outcome == market2.outcome or
                    (market1.outcome == "YES" and market2.outcome == "NO") or
                    (market1.outcome == "NO" and market2.outcome == "YES")
                )
                
                if outcome_match:
                    # Calcula diferenca de preco
                    if market1.outcome == market2.outcome:
                        price_diff = abs(market1.price - market2.price)
                    else:
                        # Outcomes opostos: compara YES com (1-NO)
                        price2_adjusted = 1 - market2.price if market2.outcome == "NO" else market2.price
                        price_diff = abs(market1.price - price2_adjusted)
                    
                    similar_pairs.append({
                        'market1': market1,
                        'market2': market2,
                        'similarity': similarity,
                        'price_diff': price_diff
                    })
    
    console.print(f"   OK {len(similar_pairs)} pares similares encontrados\n")
    
    if not similar_pairs:
        console.print("[yellow]Nenhum par similar encontrado.[/yellow]")
        console.print("[yellow]Possíveis razões:[/yellow]")
        console.print("  - Mercados muito diferentes entre exchanges")
        console.print("  - Threshold de similaridade ainda muito alto")
        console.print("  - Mercados nao se sobrepõem entre exchanges\n")
        return
    
    # Ordena por diferenca de preco (maior primeiro)
    similar_pairs.sort(key=lambda x: x['price_diff'], reverse=True)
    
    # Mostra top 20 pares
    console.print("[bold green]Top 20 Pares Mais Promissores:[/bold green]\n")
    
    table = Table(title="Pares Similares com Maior Diferenca de Preco")
    table.add_column("#", style="cyan", width=3)
    table.add_column("Exchange 1", style="yellow", width=12)
    table.add_column("Mercado 1", style="white", no_wrap=False, width=35)
    table.add_column("Preco 1", style="green", width=8)
    table.add_column("Exchange 2", style="yellow", width=12)
    table.add_column("Mercado 2", style="white", no_wrap=False, width=35)
    table.add_column("Preco 2", style="green", width=8)
    table.add_column("Diff%", style="magenta", width=7)
    table.add_column("Sim%", style="cyan", width=6)
    
    for i, pair in enumerate(similar_pairs[:20], 1):
        m1 = pair['market1']
        m2 = pair['market2']
        
        # Trunca perguntas
        q1 = m1.question[:32] + "..." if len(m1.question) > 35 else m1.question
        q2 = m2.question[:32] + "..." if len(m2.question) > 35 else m2.question
        
        # Adiciona outcome
        q1 += f" ({m1.outcome})"
        q2 += f" ({m2.outcome})"
        
        table.add_row(
            str(i),
            m1.exchange[:10],
            q1,
            f"${m1.price:.3f}",
            m2.exchange[:10],
            q2,
            f"${m2.price:.3f}",
            f"{pair['price_diff']*100:.1f}%",
            f"{pair['similarity']*100:.0f}%"
        )
    
    console.print(table)
    
    # Estatisticas
    console.print(f"\n[cyan]Estatisticas:[/cyan]")
    console.print(f"  - Total de mercados: {total_markets}")
    console.print(f"  - Pares similares encontrados: {len(similar_pairs)}")
    console.print(f"  - Maior diferenca de preco: {similar_pairs[0]['price_diff']*100:.1f}%")
    console.print(f"  - Menor diferenca de preco: {similar_pairs[-1]['price_diff']*100:.1f}%")
    
    avg_similarity = sum(p['similarity'] for p in similar_pairs) / len(similar_pairs)
    console.print(f"  - Similaridade media: {avg_similarity*100:.1f}%")
    
    # Mostra alguns detalhes do melhor par
    if similar_pairs:
        best = similar_pairs[0]
        console.print(f"\n[bold yellow]Melhor Par Encontrado:[/bold yellow]")
        console.print(f"  Exchange 1: {best['market1'].exchange}")
        console.print(f"  Pergunta 1: {best['market1'].question}")
        console.print(f"  Outcome 1: {best['market1'].outcome}")
        console.print(f"  Preco 1: ${best['market1'].price:.3f}")
        console.print(f"  Liquidez 1: ${best['market1'].liquidity:.0f}")
        console.print()
        console.print(f"  Exchange 2: {best['market2'].exchange}")
        console.print(f"  Pergunta 2: {best['market2'].question}")
        console.print(f"  Outcome 2: {best['market2'].outcome}")
        console.print(f"  Preco 2: ${best['market2'].price:.3f}")
        console.print(f"  Liquidez 2: ${best['market2'].liquidity:.0f}")
        console.print()
        console.print(f"  Similaridade: {best['similarity']*100:.1f}%")
        console.print(f"  Diferenca de preco: {best['price_diff']*100:.1f}%")
        console.print()


if __name__ == "__main__":
    asyncio.run(find_similar_markets())

