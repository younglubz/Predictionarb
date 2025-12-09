"""
Testa o Sistema Especialista de Arbitragem v2.0
"""
import asyncio
from arbitrage_expert import ArbitrageExpert
from monitor import ArbitrageMonitor

async def test_expert():
    print("\n" + "="*70)
    print("  🎯 TESTE DO SISTEMA ESPECIALISTA v2.0")
    print("="*70 + "\n")
    
    # Inicializa
    monitor = ArbitrageMonitor()
    expert = ArbitrageExpert()
    
    print("📊 Configurações do Expert:")
    print(f"   • Min Profit: {expert.min_profit_pct * 100:.1f}%")
    print(f"   • Min Liquidity: ${expert.min_liquidity}")
    print(f"   • Max Risk Score: {expert.max_risk_score}")
    print()
    
    # Busca mercados
    print("🔍 Buscando mercados...")
    await monitor.update()
    markets = monitor._cached_markets
    print(f"✅ {len(markets)} mercados encontrados\n")
    
    # Analisa com sistema especialista
    print("🧠 Analisando com Sistema Especialista...")
    opportunities = expert.find_all_opportunities(markets, monitor.matcher)
    
    print(f"\n📈 RESULTADO: {len(opportunities)} oportunidades encontradas\n")
    
    if not opportunities:
        print("❌ Nenhuma oportunidade válida encontrada")
        print("   Isso pode significar que os mercados estão eficientes")
        return
    
    # Estatísticas
    print("="*70)
    print("  📊 ESTATÍSTICAS")
    print("="*70 + "\n")
    
    # Por tipo
    by_type = {}
    for opp in opportunities:
        by_type[opp.type] = by_type.get(opp.type, 0) + 1
    
    print("Por Tipo:")
    for t, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"   • {t}: {count}")
    print()
    
    # Por estratégia
    by_strategy = {}
    for opp in opportunities:
        by_strategy[opp.strategy] = by_strategy.get(opp.strategy, 0) + 1
    
    print("Por Estratégia:")
    for s, count in sorted(by_strategy.items(), key=lambda x: -x[1]):
        print(f"   • {s}: {count}")
    print()
    
    # Métricas
    profits = [opp.net_profit_pct * 100 for opp in opportunities]
    quality_scores = [opp.quality_score for opp in opportunities]
    risk_scores = [opp.risk_score for opp in opportunities]
    
    print("Métricas:")
    print(f"   • Lucro médio: {sum(profits)/len(profits):.2f}%")
    print(f"   • Lucro máximo: {max(profits):.2f}%")
    print(f"   • Quality Score médio: {sum(quality_scores)/len(quality_scores):.1f}")
    print(f"   • Risco médio: {sum(risk_scores)/len(risk_scores)*100:.1f}%")
    print()
    
    # Top 10 oportunidades
    print("="*70)
    print("  🏆 TOP 10 OPORTUNIDADES (por Quality Score)")
    print("="*70 + "\n")
    
    for i, opp in enumerate(opportunities[:10], 1):
        print(f"#{i} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"   ID: {opp.id}")
        print(f"   Tipo: {opp.type} | Estratégia: {opp.strategy}")
        print(f"   💰 Lucro: {opp.net_profit_pct*100:.2f}% (bruto: {opp.gross_profit_pct*100:.2f}%)")
        print(f"   📊 Quality Score: {opp.quality_score:.1f}")
        print(f"   ✅ Confiança: {opp.confidence*100:.0f}%")
        print(f"   ⚠️  Risco: {opp.risk_score*100:.0f}%")
        print(f"   💧 Liquidez: {opp.liquidity_score*100:.0f}%")
        print(f"   📝 {opp.explanation}")
        print(f"   📍 Exchanges: {', '.join(m.exchange for m in opp.markets)}")
        
        if opp.warnings:
            print(f"   ⚠️  Warnings: {', '.join(opp.warnings[:2])}")
        print()
    
    # Oportunidades de baixo risco
    low_risk = [o for o in opportunities if o.risk_score < 0.3]
    print(f"\n🛡️  Oportunidades de BAIXO RISCO (<30%): {len(low_risk)}")
    
    # Oportunidades de alto lucro
    high_profit = [o for o in opportunities if o.net_profit_pct > 0.05]
    print(f"💎 Oportunidades de ALTO LUCRO (>5%): {len(high_profit)}")
    
    # Oportunidades ideais
    ideal = [o for o in opportunities if o.risk_score < 0.3 and o.net_profit_pct > 0.02]
    print(f"⭐ Oportunidades IDEAIS (baixo risco + bom lucro): {len(ideal)}")
    
    print("\n" + "="*70)
    print("  ✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(test_expert())

