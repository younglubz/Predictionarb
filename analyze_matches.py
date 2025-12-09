"""Script para analisar matches e entender por que não há oportunidades"""
import asyncio
from monitor import ArbitrageMonitor

async def main():
    print("\n" + "="*60)
    print("  ANÁLISE DE MATCHES - Por que não há oportunidades?")
    print("="*60 + "\n")
    
    monitor = ArbitrageMonitor()
    
    # Busca mercados
    print("📊 Buscando mercados...")
    markets = await monitor.fetch_all_markets()
    print(f"✓ {len(markets)} mercados encontrados\n")
    
    # Encontra matches
    print("🔍 Buscando matches...")
    matches = monitor.matcher.find_matching_events(markets)
    print(f"✓ {len(matches)} matches encontrados\n")
    
    if len(matches) == 0:
        print("❌ Nenhum match encontrado!")
        return
    
    # Analisa primeiros matches
    print("="*60)
    print("  ANÁLISE DOS PRIMEIROS 10 MATCHES")
    print("="*60 + "\n")
    
    for i, (market1, market2) in enumerate(matches[:10], 1):
        print(f"\n━━━━ MATCH #{i} ━━━━")
        
        # Calcula similaridade
        similarity = monitor.matcher.calculate_enhanced_similarity(
            market1.question,
            market2.question
        )
        
        print(f"\n📝 Market 1: {market1.exchange}")
        print(f"   Q: {market1.question[:70]}...")
        print(f"   Price: ${market1.price:.4f}")
        print(f"   Liquidity: ${market1.liquidity:.0f}")
        
        print(f"\n📝 Market 2: {market2.exchange}")
        print(f"   Q: {market2.question[:70]}...")
        print(f"   Price: ${market2.price:.4f}")
        print(f"   Liquidity: ${market2.liquidity:.0f}")
        
        print(f"\n📊 Similaridade: {similarity*100:.1f}%")
        
        # Calcula diferença de preço
        price_diff = abs(market1.price - market2.price)
        price_diff_pct = (price_diff / min(market1.price, market2.price)) * 100
        
        print(f"💰 Diferença de preço: ${price_diff:.4f} ({price_diff_pct:.1f}%)")
        
        # Tenta calcular arbitragem
        confidence = similarity
        opp = monitor.engine.calculate_arbitrage(market1, market2, confidence)
        
        if opp:
            print(f"✅ OPORTUNIDADE! Lucro: {opp.profit_pct*100:.2f}%")
        else:
            print("❌ SEM OPORTUNIDADE")
            
            # Diagnóstico
            print("\n🔍 Diagnóstico:")
            
            # Valida equivalência
            equivalent, validation = monitor.engine.validator.validate_equivalence(market1, market2)
            if not equivalent:
                print(f"   • Validação falhou: {validation.get('reason', 'unknown')}")
                if 'country1' in validation:
                    print(f"     - País 1: {validation['country1']}")
                    print(f"     - País 2: {validation['country2']}")
            
            # Verifica liquidez
            if market1.liquidity < monitor.engine.min_liquidity:
                print(f"   • Market 1: liquidez baixa (${market1.liquidity:.0f} < ${monitor.engine.min_liquidity})")
            if market2.liquidity < monitor.engine.min_liquidity:
                print(f"   • Market 2: liquidez baixa (${market2.liquidity:.0f} < ${monitor.engine.min_liquidity})")
            
            # Verifica lucro
            if price_diff_pct < monitor.engine.min_profit * 100:
                print(f"   • Diferença de preço muito baixa ({price_diff_pct:.1f}% < {monitor.engine.min_profit*100:.1f}%)")
    
    print("\n" + "="*60)
    print("  RESUMO")
    print("="*60 + "\n")
    print(f"Total de matches: {len(matches)}")
    print(f"Oportunidades: {len(monitor.opportunities)}")
    print(f"\nConfiguração atual:")
    print(f"  • Threshold: {monitor.matcher.similarity_threshold*100:.0f}%")
    print(f"  • Lucro mínimo: {monitor.engine.min_profit*100:.1f}%")
    print(f"  • Liquidez mínima: ${monitor.engine.min_liquidity:.0f}")
    print()

if __name__ == "__main__":
    asyncio.run(main())

