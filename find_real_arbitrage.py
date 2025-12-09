# -*- coding: utf-8 -*-
"""Busca oportunidades REAIS de arbitragem verificando equivalencia rigorosa"""
import asyncio
from monitor import ArbitrageMonitor
from matcher import EventMatcher
from market_validator import MarketValidator
from rich.console import Console
from rich.table import Table
from datetime import datetime, timedelta, timezone

console = Console()


async def find_real_arbitrage():
    console.print("\n[bold cyan]Buscando Oportunidades REAIS de Arbitragem[/bold cyan]\n")
    
    # Inicializa
    monitor = ArbitrageMonitor()
    matcher = EventMatcher()
    validator = MarketValidator()
    
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
    
    # Filtra mercados viáveis
    console.print("[yellow]2. Filtrando mercados viaveis...[/yellow]")
    viable_markets = []
    
    for market in all_markets:
        # Criterios minimos
        # Checa expiracao
        is_expired = False
        if market.expires_at:
            try:
                now = datetime.now(timezone.utc)
                is_expired = market.expires_at < now
            except:
                pass
        
        if (market.price > 0.05 and market.price < 0.95 and  # Precos razoaveis
            market.liquidity > 50 and  # Liquidez minima
            not is_expired):  # Nao expirado
            viable_markets.append(market)
    
    console.print(f"   {len(viable_markets)} mercados viaveis\n")
    
    # Busca pares equivalentes
    console.print("[yellow]3. Buscando mercados equivalentes (threshold 70%)...[/yellow]")
    
    equivalent_pairs = []
    checked = set()
    
    for i, m1 in enumerate(viable_markets):
        for m2 in viable_markets[i+1:]:
            # Mesma exchange = skip
            if m1.exchange == m2.exchange:
                continue
            
            # Ja checou = skip
            pair_key = tuple(sorted([m1.market_id, m2.market_id]))
            if pair_key in checked:
                continue
            checked.add(pair_key)
            
            # Similaridade alta
            sim = matcher.calculate_similarity(m1.question, m2.question)
            if sim < 0.70:
                continue
            
            # Valida equivalencia
            is_valid, reason = validator.validate_equivalence(m1, m2)
            if not is_valid:
                continue
            
            # Calcula arbitragem
            # Se outcomes iguais: compara precos diretos
            # Se outcomes opostos: compara YES com (1-NO)
            if m1.outcome == m2.outcome:
                # Mesmo outcome: compra mais barato, vende mais caro
                if m1.price < m2.price:
                    buy_market = m1
                    sell_market = m2
                else:
                    buy_market = m2
                    sell_market = m1
                
                gross_profit = sell_market.price - buy_market.price
            else:
                # Outcomes opostos: arbitragem classica
                # Compra YES em um, compra NO em outro
                if m1.outcome == "YES":
                    yes_market = m1
                    no_market = m2
                else:
                    yes_market = m2
                    no_market = m1
                
                # Custo total: price_yes + price_no
                total_cost = yes_market.price + no_market.price
                
                # Lucro bruto: 1 - custo (paga $1 se correto)
                gross_profit = 1.0 - total_cost
                
                buy_market = yes_market
                sell_market = no_market
            
            # Calcula taxas
            fee1 = monitor.engine.config.EXCHANGE_FEES.get(m1.exchange, 0.02)
            fee2 = monitor.engine.config.EXCHANGE_FEES.get(m2.exchange, 0.02)
            
            total_fees = (buy_market.price * fee1) + (sell_market.price * fee2)
            net_profit = gross_profit - total_fees
            
            # Se lucro positivo
            if net_profit > 0:
                equivalent_pairs.append({
                    'market1': m1,
                    'market2': m2,
                    'similarity': sim,
                    'gross_profit': gross_profit,
                    'total_fees': total_fees,
                    'net_profit': net_profit,
                    'net_profit_pct': (net_profit / buy_market.price) * 100 if buy_market.price > 0 else 0
                })
    
    console.print(f"   {len(equivalent_pairs)} oportunidades encontradas\n")
    
    if not equivalent_pairs:
        console.print("[yellow]Nenhuma oportunidade encontrada.[/yellow]\n")
        console.print("[cyan]Motivos possiveis:[/cyan]")
        console.print("  - Mercados eficientes (precos ja arbitrados)")
        console.print("  - Threshold de similaridade muito alto")
        console.print("  - Taxas das exchanges consomem todo o lucro")
        console.print("  - Falta de mercados equivalentes entre exchanges\n")
        
        # Mostra alguns mercados similares que NAO passaram
        console.print("[yellow]Exemplos de pares similares que NAO sao arbitragem:[/yellow]\n")
        
        examples = []
        for i, m1 in enumerate(viable_markets[:50]):
            for m2 in viable_markets[i+1:i+10]:
                if m1.exchange == m2.exchange:
                    continue
                
                sim = matcher.calculate_similarity(m1.question, m2.question)
                if sim >= 0.60:
                    examples.append((m1, m2, sim))
                    if len(examples) >= 5:
                        break
            if len(examples) >= 5:
                break
        
        for m1, m2, sim in examples:
            console.print(f"  Similaridade: {sim*100:.0f}%")
            console.print(f"    {m1.exchange}: {m1.question[:60]}... ({m1.outcome}) = ${m1.price:.3f}")
            console.print(f"    {m2.exchange}: {m2.question[:60]}... ({m2.outcome}) = ${m2.price:.3f}")
            console.print()
        
        return
    
    # Ordena por lucro liquido %
    equivalent_pairs.sort(key=lambda x: x['net_profit_pct'], reverse=True)
    
    # Mostra oportunidades
    console.print("[bold green]OPORTUNIDADES DE ARBITRAGEM ENCONTRADAS![/bold green]\n")
    
    table = Table(title="Oportunidades Reais de Arbitragem")
    table.add_column("#", style="cyan", width=3)
    table.add_column("Exchange A", style="yellow", width=12)
    table.add_column("Preco A", style="green", width=9)
    table.add_column("Exchange B", style="yellow", width=12)
    table.add_column("Preco B", style="green", width=9)
    table.add_column("Lucro Bruto", style="magenta", width=11)
    table.add_column("Taxas", style="red", width=8)
    table.add_column("Lucro Liquido", style="green", width=13)
    table.add_column("ROI%", style="cyan", width=7)
    
    for i, opp in enumerate(equivalent_pairs[:10], 1):
        table.add_row(
            str(i),
            opp['market1'].exchange[:10],
            f"${opp['market1'].price:.3f}",
            opp['market2'].exchange[:10],
            f"${opp['market2'].price:.3f}",
            f"${opp['gross_profit']:.3f}",
            f"${opp['total_fees']:.3f}",
            f"${opp['net_profit']:.3f}",
            f"{opp['net_profit_pct']:.1f}%"
        )
    
    console.print(table)
    
    # Detalhes da melhor oportunidade
    best = equivalent_pairs[0]
    console.print(f"\n[bold yellow]Melhor Oportunidade:[/bold yellow]\n")
    console.print(f"Mercado 1:")
    console.print(f"  Exchange: {best['market1'].exchange}")
    console.print(f"  Pergunta: {best['market1'].question}")
    console.print(f"  Outcome: {best['market1'].outcome}")
    console.print(f"  Preco: ${best['market1'].price:.3f}")
    console.print(f"  Liquidez: ${best['market1'].liquidity:.0f}")
    console.print()
    console.print(f"Mercado 2:")
    console.print(f"  Exchange: {best['market2'].exchange}")
    console.print(f"  Pergunta: {best['market2'].question}")
    console.print(f"  Outcome: {best['market2'].outcome}")
    console.print(f"  Preco: ${best['market2'].price:.3f}")
    console.print(f"  Liquidez: ${best['market2'].liquidity:.0f}")
    console.print()
    console.print(f"Analise:")
    console.print(f"  Similaridade: {best['similarity']*100:.1f}%")
    console.print(f"  Lucro Bruto: ${best['gross_profit']:.3f} ({best['gross_profit']*100:.1f}%)")
    console.print(f"  Taxas: ${best['total_fees']:.3f}")
    console.print(f"  Lucro Liquido: ${best['net_profit']:.3f} ({best['net_profit_pct']:.1f}% ROI)")
    console.print()


if __name__ == "__main__":
    asyncio.run(find_real_arbitrage())

