# -*- coding: utf-8 -*-
"""Busca oportunidades de arbitragem - versao simples sem rich"""
import asyncio
from monitor import ArbitrageMonitor
from matcher_improved import ImprovedEventMatcher
from datetime import datetime, timezone
import json


async def find_opportunities():
    print("\n=== BUSCANDO OPORTUNIDADES DE ARBITRAGEM ===\n")
    
    monitor = ArbitrageMonitor()
    
    # Busca mercados
    print("1. Buscando mercados...")
    all_markets = []
    
    for exchange in monitor.exchanges:
        try:
            markets = await exchange.fetch_markets()
            all_markets.extend(markets)
            print(f"   {exchange.name}: {len(markets)} mercados")
        except Exception as e:
            print(f"   ERRO em {exchange.name}: {e}")
    
    print(f"\n   Total: {len(all_markets)} mercados\n")
    
    # Filtra mercados viáveis
    print("2. Filtrando mercados viaveis...")
    now = datetime.now(timezone.utc)
    viable_markets = []
    
    for market in all_markets:
        # Ignora expirados
        if market.expires_at:
            expires_aware = market.expires_at if market.expires_at.tzinfo else market.expires_at.replace(tzinfo=timezone.utc)
            if expires_aware < now:
                continue
        
        # Ignora baixa liquidez
        if market.liquidity < 50:
            continue
        
        # Ignora precos extremos
        if market.price <= 0.02 or market.price >= 0.98:
            continue
        
        viable_markets.append(market)
    
    print(f"   Viaveis: {len(viable_markets)} mercados\n")
    
    # Agrupa por exchange
    by_exchange = {}
    for market in viable_markets:
        if market.exchange not in by_exchange:
            by_exchange[market.exchange] = []
        by_exchange[market.exchange].append(market)
    
    for exchange, markets in by_exchange.items():
        print(f"   {exchange}: {len(markets)}")
    
    # Busca pares similares
    print("\n3. Buscando pares similares (Matcher Melhorado)...")
    # Threshold 70%, max 7 dias de diferença entre datas
    matcher = ImprovedEventMatcher(similarity_threshold=0.70, max_date_diff_days=7)
    
    similar_pairs = []
    for i, m1 in enumerate(viable_markets):
        if i % 100 == 0:
            print(f"   Processando {i}/{len(viable_markets)}...")
        
        for m2 in viable_markets[i+1:]:
            if m1.exchange == m2.exchange:
                continue
            
            is_match, similarity, details = matcher.are_markets_equivalent(m1, m2)
            
            if is_match:
                similar_pairs.append((m1, m2, similarity))
    
    print(f"\n   Pares similares: {len(similar_pairs)}\n")
    
    # Calcula arbitragens
    print("4. Calculando oportunidades...")
    opportunities = []
    
    for m1, m2, similarity in similar_pairs:
        price_diff = abs(m1.price - m2.price)
        
        if price_diff < 0.015:  # Minimo 1.5 centavos
            continue
        
        if m1.price < m2.price:
            buy_market, sell_market = m1, m2
        else:
            buy_market, sell_market = m2, m1
        
        gross_profit = sell_market.price - buy_market.price
        gross_profit_pct = (gross_profit / buy_market.price) * 100
        
        # Taxas (7% total tipicamente)
        fees = 0.07
        net_profit = gross_profit - (buy_market.price * fees)
        net_profit_pct = (net_profit / buy_market.price) * 100
        
        # So considera se lucro > 1%
        if net_profit_pct > 1.0:
            opportunities.append({
                "buy_exchange": buy_market.exchange,
                "sell_exchange": sell_market.exchange,
                "buy_question": buy_market.question,
                "sell_question": sell_market.question,
                "buy_price": buy_market.price,
                "sell_price": sell_market.price,
                "price_diff": price_diff,
                "gross_profit_pct": gross_profit_pct,
                "net_profit_pct": net_profit_pct,
                "similarity": similarity,
                "buy_url": buy_market.url,
                "sell_url": sell_market.url
            })
    
    opportunities.sort(key=lambda x: x["net_profit_pct"], reverse=True)
    
    print(f"\n=== {len(opportunities)} OPORTUNIDADES ENCONTRADAS ===\n")
    
    if opportunities:
        print("TOP 5 OPORTUNIDADES:\n")
        for i, opp in enumerate(opportunities[:5], 1):
            print(f"{i}. LUCRO: {opp['net_profit_pct']:.2f}%")
            print(f"   Comprar: [{opp['buy_exchange']}] @ ${opp['buy_price']:.3f}")
            print(f"   Vender: [{opp['sell_exchange']}] @ ${opp['sell_price']:.3f}")
            print(f"   Questao (Comprar): {opp['buy_question'][:60]}...")
            print(f"   Questao (Vender): {opp['sell_question'][:60]}...")
            print(f"   Similaridade: {opp['similarity']:.1%}")
            print()
        
        # Salva
        with open("opportunities.json", "w", encoding="utf-8") as f:
            json.dump(opportunities, f, indent=2, ensure_ascii=False)
        
        print(f"Salvo em opportunities.json")
    else:
        print("Nenhuma oportunidade encontrada com os criterios atuais.")
    
    return opportunities


if __name__ == "__main__":
    asyncio.run(find_opportunities())

