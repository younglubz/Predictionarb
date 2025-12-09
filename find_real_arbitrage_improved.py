# -*- coding: utf-8 -*-
"""Encontra oportunidades reais de arbitragem com matcher melhorado"""
import asyncio
from monitor import ArbitrageMonitor
from matcher_improved import ImprovedEventMatcher
from rich.console import Console
from rich.table import Table
from datetime import datetime, timezone

console = Console()


async def find_real_arbitrage_improved():
    console.print("\n[bold cyan]Buscando Oportunidades Reais de Arbitragem[/bold cyan]")
    console.print("[yellow]Usando Matcher Melhorado com Detecção de Sinônimos[/yellow]\n")
    
    # Inicializa monitor
    monitor = ArbitrageMonitor()
    
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
    console.print(f"\n   [green]OK {total_markets} mercados encontrados[/green]\n")
    
    # Filtra mercados viáveis
    console.print("[yellow]2. Filtrando mercados viáveis...[/yellow]")
    now = datetime.now(timezone.utc)
    viable_markets = []
    
    for market in all_markets:
        # Ignora mercados expirados
        if market.expires_at:
            # Torna ambos timezone-aware
            expires_aware = market.expires_at if market.expires_at.tzinfo else market.expires_at.replace(tzinfo=timezone.utc)
            if expires_aware < now:
                continue
        
        # Ignora mercados com liquidez muito baixa
        if market.liquidity < 10:  # Muito relaxado
            continue
        
        # Ignora preços extremos
        if market.price <= 0.01 or market.price >= 0.99:
            continue
        
        viable_markets.append(market)
    
    console.print(f"   [green]✓ {len(viable_markets)} mercados viáveis[/green]\n")
    
    # Agrupa por exchange
    by_exchange = {}
    for market in viable_markets:
        if market.exchange not in by_exchange:
            by_exchange[market.exchange] = []
        by_exchange[market.exchange].append(market)
    
    console.print("[cyan]Mercados viáveis por exchange:[/cyan]")
    for exchange, markets in by_exchange.items():
        console.print(f"  - {exchange}: {len(markets)} mercados")
    
    # Usa matcher melhorado
    console.print("\n[yellow]3. Buscando pares similares (Matcher Melhorado)...[/yellow]")
    matcher = ImprovedEventMatcher(similarity_threshold=0.60)  # 60% para ser mais criterioso
    
    similar_pairs = []
    checked = set()
    
    total_comparisons = 0
    for i, market1 in enumerate(viable_markets):
        for j, market2 in enumerate(viable_markets[i+1:], i+1):
            total_comparisons += 1
            
            # Skip mesma exchange
            if market1.exchange == market2.exchange:
                continue
            
            pair_key = tuple(sorted([
                f"{market1.exchange}:{market1.market_id}",
                f"{market2.exchange}:{market2.market_id}"
            ]))
            
            if pair_key in checked:
                continue
            
            checked.add(pair_key)
            
            is_match, similarity, details = matcher.are_markets_equivalent(market1, market2)
            
            if is_match:
                similar_pairs.append((market1, market2, similarity, details))
    
    console.print(f"   [green]✓ {len(similar_pairs)} pares similares encontrados[/green]")
    console.print(f"   [dim](comparou {total_comparisons} pares)[/dim]\n")
    
    # Calcula arbitragens
    console.print("[yellow]4. Calculando oportunidades de arbitragem...[/yellow]\n")
    
    arbitrage_opportunities = []
    
    for market1, market2, similarity, details in similar_pairs:
        # Calcula lucro potencial
        price_diff = abs(market1.price - market2.price)
        
        # Ignora diferenças muito pequenas
        if price_diff < 0.01:  # Menos de 1 centavo
            continue
        
        # Calcula lucro percentual
        if market1.price < market2.price:
            buy_market = market1
            sell_market = market2
            buy_price = market1.price
            sell_price = market2.price
        else:
            buy_market = market2
            sell_market = market1
            buy_price = market2.price
            sell_price = market1.price
        
        # Lucro bruto
        gross_profit = sell_price - buy_price
        gross_profit_pct = (gross_profit / buy_price) * 100
        
        # Considera taxas (5% PredictIt, 2% Polymarket tipicamente)
        fees = 0.05 + 0.02  # 7% total
        net_profit = gross_profit - (buy_price * fees)
        net_profit_pct = (net_profit / buy_price) * 100
        
        # Só considera se lucro líquido > 0.5%
        if net_profit_pct > 0.5:
            arbitrage_opportunities.append({
                "buy_exchange": buy_market.exchange,
                "sell_exchange": sell_market.exchange,
                "buy_question": buy_market.question,
                "sell_question": sell_market.question,
                "buy_price": buy_price,
                "sell_price": sell_price,
                "price_diff": price_diff,
                "gross_profit_pct": gross_profit_pct,
                "net_profit_pct": net_profit_pct,
                "similarity": similarity,
                "liquidity_buy": buy_market.liquidity,
                "liquidity_sell": sell_market.liquidity,
                "url_buy": buy_market.url,
                "url_sell": sell_market.url,
                "entities": details.get("entities1", {})
            })
    
    # Ordena por lucro líquido
    arbitrage_opportunities.sort(key=lambda x: x["net_profit_pct"], reverse=True)
    
    console.print(f"[bold green]{len(arbitrage_opportunities)} OPORTUNIDADES DE ARBITRAGEM ENCONTRADAS![/bold green]\n")
    
    # Mostra top 10
    if arbitrage_opportunities:
        table = Table(title=f"🚀 Top {min(10, len(arbitrage_opportunities))} Oportunidades de Arbitragem")
        table.add_column("Lucro", style="green bold", justify="right")
        table.add_column("Comprar", style="cyan")
        table.add_column("Vender", style="yellow")
        table.add_column("Preços", style="white")
        table.add_column("Similaridade", style="magenta", justify="right")
        
        for i, opp in enumerate(arbitrage_opportunities[:10], 1):
            table.add_row(
                f"{opp['net_profit_pct']:.2f}%",
                f"[{opp['buy_exchange']}]\n{opp['buy_question'][:40]}...",
                f"[{opp['sell_exchange']}]\n{opp['sell_question'][:40]}...",
                f"${opp['buy_price']:.3f} → ${opp['sell_price']:.3f}",
                f"{opp['similarity']:.1%}"
            )
        
        console.print(table)
        console.print()
        
        # Detalhes da melhor oportunidade
        best = arbitrage_opportunities[0]
        console.print("[bold cyan]💎 MELHOR OPORTUNIDADE:[/bold cyan]")
        console.print(f"   Lucro Líquido: [bold green]{best['net_profit_pct']:.2f}%[/bold green]")
        console.print(f"   Comprar: [{best['buy_exchange']}] @ ${best['buy_price']:.3f}")
        console.print(f"   Vender: [{best['sell_exchange']}] @ ${best['sell_price']:.3f}")
        console.print(f"   Diferença: ${best['price_diff']:.3f}")
        console.print(f"   Similaridade: {best['similarity']:.1%}")
        console.print(f"\n   Questão (Comprar): {best['buy_question']}")
        console.print(f"   Questão (Vender): {best['sell_question']}")
        console.print(f"\n   URL Comprar: {best['url_buy']}")
        console.print(f"   URL Vender: {best['url_sell']}")
        
        # Salva em arquivo
        import json
        with open("arbitrage_opportunities.json", "w", encoding="utf-8") as f:
            json.dump(arbitrage_opportunities, f, indent=2, ensure_ascii=False, default=str)
        
        console.print(f"\n[green]Oportunidades salvas em arbitrage_opportunities.json[/green]")
    else:
        console.print("[yellow]Nenhuma oportunidade de arbitragem encontrada no momento.[/yellow]")
        console.print("[dim]Dica: Tente ajustar o threshold de similaridade ou os filtros de lucro.[/dim]")
    
    return arbitrage_opportunities


if __name__ == "__main__":
    asyncio.run(find_real_arbitrage_improved())

