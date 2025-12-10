# -*- coding: utf-8 -*-
"""Verifica matches da Polymarket e mostra opções específicas YES/NO"""
import asyncio
from monitor import ArbitrageMonitor
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime

console = Console()


def get_outcome_details(market):
    """Extrai detalhes específicos do outcome"""
    exchange_lower = market.exchange.lower()
    question = market.question
    
    # Para Polymarket: verifica se há indicação específica
    if 'polymarket' in exchange_lower:
        # Polymarket geralmente tem "Yes" ou "No" no outcome_name
        # Mas o outcome normalizado é YES/NO
        if market.outcome == 'YES':
            return "YES (Yes)"
        elif market.outcome == 'NO':
            return "NO (No)"
        else:
            return market.outcome
    
    # Para PredictIt: extrai contrato
    if 'predictit' in exchange_lower:
        parts = question.split(' - ')
        if len(parts) >= 2:
            contract = parts[-1].strip()
            return f"{market.outcome} ({contract})"
        return market.outcome
    
    # Para Manifold: sempre YES/NO
    if 'manifold' in exchange_lower:
        return f"{market.outcome}"
    
    # Para Kalshi: YES/NO
    if 'kalshi' in exchange_lower:
        return f"{market.outcome}"
    
    return market.outcome


async def check_polymarket_matches():
    """Verifica matches envolvendo Polymarket"""
    console.print("\n[bold cyan]Verificando Matches da Polymarket[/bold cyan]\n")
    
    monitor = ArbitrageMonitor()
    
    # 1. Busca mercados
    console.print("[yellow]1. Buscando mercados...[/yellow]")
    markets = await monitor.fetch_all_markets()
    
    # Agrupa por exchange
    by_exchange = {}
    for m in markets:
        ex = m.exchange.lower()
        if ex not in by_exchange:
            by_exchange[ex] = []
        by_exchange[ex].append(m)
    
    console.print(f"\n[green]Mercados encontrados:[/green]")
    for ex, m_list in by_exchange.items():
        console.print(f"  • {ex}: {len(m_list)} mercados")
    
    # 2. Encontra matches
    console.print(f"\n[yellow]2. Buscando matches...[/yellow]")
    matches = monitor.matcher.find_matching_events(markets)
    console.print(f"[green]Total de matches: {len(matches)}[/green]\n")
    
    # 3. Filtra matches envolvendo Polymarket
    polymarket_matches = []
    for m1, m2 in matches:
        ex1 = m1.exchange.lower()
        ex2 = m2.exchange.lower()
        if 'polymarket' in ex1 or 'polymarket' in ex2:
            polymarket_matches.append((m1, m2))
    
    console.print(f"[green]Matches envolvendo Polymarket: {len(polymarket_matches)}[/green]\n")
    
    if not polymarket_matches:
        console.print("[red]❌ Nenhum match encontrado envolvendo Polymarket![/red]\n")
        console.print("[yellow]Possíveis razões:[/yellow]")
        console.print("  • Mercados da Polymarket não têm equivalentes em outras exchanges")
        console.print("  • Threshold de similaridade muito alto")
        console.print("  • Diferenças nas datas de expiração")
        console.print("  • Diferenças nos países/estados/candidatos")
        return
    
    # 4. Mostra matches com detalhes
    table = Table(title="Matches da Polymarket com Opções Específicas")
    table.add_column("Polymarket", style="cyan", no_wrap=False)
    table.add_column("Opção Polymarket", style="yellow", justify="center")
    table.add_column("Outra Exchange", style="magenta", no_wrap=False)
    table.add_column("Opção Outra", style="yellow", justify="center")
    table.add_column("Similaridade", style="green", justify="right")
    table.add_column("Preço Poly", style="blue", justify="right")
    table.add_column("Preço Outra", style="blue", justify="right")
    table.add_column("Diferença", style="red", justify="right")
    
    for m1, m2 in polymarket_matches[:50]:  # Mostra top 50
        # Identifica qual é Polymarket
        if 'polymarket' in m1.exchange.lower():
            poly_market = m1
            other_market = m2
        else:
            poly_market = m2
            other_market = m1
        
        # Calcula similaridade
        similarity = monitor.matcher.calculate_enhanced_similarity(
            poly_market.question,
            other_market.question
        )
        
        # Calcula diferença de preço
        if poly_market.outcome == other_market.outcome:
            price_diff = abs(poly_market.price - other_market.price)
        else:
            # Outcomes opostos
            if poly_market.outcome == 'YES':
                price_diff = abs(poly_market.price - (1 - other_market.price))
            else:
                price_diff = abs((1 - poly_market.price) - other_market.price)
        
        # Opções específicas
        poly_option = get_outcome_details(poly_market)
        other_option = get_outcome_details(other_market)
        
        table.add_row(
            poly_market.question[:60] + "..." if len(poly_market.question) > 60 else poly_market.question,
            poly_option,
            other_market.question[:60] + "..." if len(other_market.question) > 60 else other_market.question,
            other_option,
            f"{similarity:.1%}",
            f"${poly_market.price:.3f}",
            f"${other_market.price:.3f}",
            f"{price_diff:.1%}"
        )
    
    console.print(table)
    
    # 5. Verifica por que não geram oportunidades
    console.print(f"\n[yellow]3. Verificando por que não geram oportunidades...[/yellow]\n")
    
    from arbitrage import ArbitrageEngine
    from config import MIN_ARBITRAGE_PROFIT, MIN_LIQUIDITY
    engine = ArbitrageEngine()
    
    opportunities = []
    rejected_reasons = []
    
    for m1, m2 in polymarket_matches:
        if 'polymarket' in m1.exchange.lower():
            poly_market = m1
            other_market = m2
        else:
            poly_market = m2
            other_market = m1
        
        similarity = monitor.matcher.calculate_enhanced_similarity(
            poly_market.question,
            other_market.question
        )
        
        # Verifica razões de rejeição
        reason = []
        
        # 1. Liquidez
        if poly_market.liquidity < MIN_LIQUIDITY:
            reason.append(f"Liquidez Poly baixa: ${poly_market.liquidity:.0f} < ${MIN_LIQUIDITY}")
        if other_market.liquidity < MIN_LIQUIDITY:
            reason.append(f"Liquidez {other_market.exchange} baixa: ${other_market.liquidity:.0f} < ${MIN_LIQUIDITY}")
        
        # 2. Preços válidos
        if poly_market.price <= 0.01 or poly_market.price >= 0.99:
            reason.append(f"Preço Poly inválido: ${poly_market.price:.3f}")
        if other_market.price <= 0.01 or other_market.price >= 0.99:
            reason.append(f"Preço {other_market.exchange} inválido: ${other_market.price:.3f}")
        
        # 3. Diferença de preço
        if poly_market.outcome == other_market.outcome:
            price_diff = abs(poly_market.price - other_market.price)
        else:
            if poly_market.outcome == 'YES':
                price_diff = abs(poly_market.price - (1 - other_market.price))
            else:
                price_diff = abs((1 - poly_market.price) - other_market.price)
        
        # 4. Valida equivalência
        from market_validator import MarketValidator
        validator = MarketValidator()
        equivalent, validation = validator.validate_equivalence(poly_market, other_market)
        if not equivalent:
            reason.append(f"Validação falhou: {validation.get('issues', [])}")
        
        # Tenta calcular arbitragem
        opp = engine.calculate_arbitrage(poly_market, other_market, similarity)
        if opp:
            opportunities.append(opp)
        else:
            if not reason:
                # Calcula lucro bruto para ver se é suficiente
                if poly_market.price < other_market.price:
                    buy_price = poly_market.price
                    sell_price = other_market.price
                else:
                    buy_price = other_market.price
                    sell_price = poly_market.price
                
                profit_abs = sell_price - buy_price
                profit_pct = profit_abs / buy_price if buy_price > 0 else 0
                
                if profit_pct < MIN_ARBITRAGE_PROFIT:
                    reason.append(f"Lucro muito baixo: {profit_pct:.2%} < {MIN_ARBITRAGE_PROFIT:.2%}")
            
            rejected_reasons.append({
                'poly': poly_market.question[:50],
                'other': other_market.exchange,
                'poly_option': get_outcome_details(poly_market),
                'other_option': get_outcome_details(other_market),
                'poly_price': poly_market.price,
                'other_price': other_market.price,
                'poly_liq': poly_market.liquidity,
                'other_liq': other_market.liquidity,
                'reasons': reason
            })
    
    console.print(f"[green]Oportunidades encontradas: {len(opportunities)}[/green]\n")
    
    if rejected_reasons:
        console.print(f"[yellow]Matches rejeitados: {len(rejected_reasons)}[/yellow]\n")
        reject_table = Table(title="Razões de Rejeição dos Matches")
        reject_table.add_column("Polymarket", style="cyan", no_wrap=False)
        reject_table.add_column("Opção Poly", style="yellow", justify="center")
        reject_table.add_column("Outra Exchange", style="magenta")
        reject_table.add_column("Opção Outra", style="yellow", justify="center")
        reject_table.add_column("Preço Poly", style="blue", justify="right")
        reject_table.add_column("Preço Outra", style="blue", justify="right")
        reject_table.add_column("Liq Poly", style="green", justify="right")
        reject_table.add_column("Liq Outra", style="green", justify="right")
        reject_table.add_column("Razão", style="red", no_wrap=False)
        
        for r in rejected_reasons[:20]:
            reject_table.add_row(
                r['poly'],
                r['poly_option'],
                r['other'],
                r['other_option'],
                f"${r['poly_price']:.3f}",
                f"${r['other_price']:.3f}",
                f"${r['poly_liq']:.0f}",
                f"${r['other_liq']:.0f}",
                "; ".join(r['reasons']) if r['reasons'] else "Desconhecido"
            )
        
        console.print(reject_table)
    
    if opportunities:
        opp_table = Table(title="Oportunidades da Polymarket")
        opp_table.add_column("Polymarket", style="cyan")
        opp_table.add_column("Opção Poly", style="yellow", justify="center")
        opp_table.add_column("Outra Exchange", style="magenta")
        opp_table.add_column("Opção Outra", style="yellow", justify="center")
        opp_table.add_column("Lucro %", style="green", justify="right")
        opp_table.add_column("Confiança", style="blue", justify="right")
        
        for opp in opportunities[:20]:
            if 'polymarket' in opp.market_buy.exchange.lower():
                poly_market = opp.market_buy
                other_market = opp.market_sell
            else:
                poly_market = opp.market_sell
                other_market = opp.market_buy
            
            poly_option = get_outcome_details(poly_market)
            other_option = get_outcome_details(other_market)
            
            opp_table.add_row(
                poly_market.question[:50] + "..." if len(poly_market.question) > 50 else poly_market.question,
                poly_option,
                other_market.exchange,
                other_option,
                f"{opp.profit_pct:.2%}",
                f"{opp.confidence:.1%}"
            )
        
        console.print(opp_table)
    else:
        console.print("[red]❌ Nenhuma oportunidade encontrada mesmo com matches![/red]\n")
        console.print("[yellow]Razões possíveis:[/yellow]")
        console.print("  • Diferença de preço muito pequena (menor que MIN_ARBITRAGE_PROFIT)")
        console.print("  • Liquidez muito baixa (menor que MIN_LIQUIDITY)")
        console.print("  • Taxas de transação eliminam o lucro")
        console.print("  • Mercados muito eficientes (preços já convergiram)")


if __name__ == "__main__":
    asyncio.run(check_polymarket_matches())

