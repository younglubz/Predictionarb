"""Debug: Por que matches não viram oportunidades?"""
import asyncio
from monitor import ArbitrageMonitor
from config import UPDATE_INTERVAL

async def main():
    monitor = ArbitrageMonitor()
    
    print("\n🔍 DIAGNÓSTICO: Por que não há oportunidades?\n")
    print("=" * 60)
    
    # Busca mercados
    print("\n1️⃣ Buscando mercados...")
    markets = await monitor.fetch_all_markets()
    print(f"   ✅ {len(markets)} mercados encontrados")
    
    # Encontra matches
    print("\n2️⃣ Encontrando matches...")
    matches = monitor.matcher.find_matching_events(markets)
    print(f"   ✅ {len(matches)} pares matchados")
    
    # Calcula confiança e tenta criar oportunidades
    print("\n3️⃣ Tentando criar oportunidades...")
    market_pairs = []
    blocked_count = 0
    blocked_reasons = {}
    
    for market1, market2 in matches[:20]:  # Testa apenas primeiros 20
        confidence = monitor.matcher.calculate_enhanced_similarity(
            market1.question,
            market2.question
        )
        market_pairs.append((market1, market2, confidence))
        
        # Testa validação
        equivalent, validation = monitor.engine.validator.validate_equivalence(market1, market2)
        
        if not equivalent:
            blocked_count += 1
            reason = ", ".join(validation.get("issues", ["Unknown"]))
            blocked_reasons[reason] = blocked_reasons.get(reason, 0) + 1
            
            if blocked_count <= 5:  # Mostra primeiros 5
                print(f"\n   ❌ Match {blocked_count} BLOQUEADO:")
                print(f"      {market1.exchange}: {market1.question[:60]}...")
                print(f"      {market2.exchange}: {market2.question[:60]}...")
                print(f"      Similaridade (Improved): {confidence:.2%}")
                print(f"      Razão: {reason}")
    
    # Encontra oportunidades reais
    opportunities = monitor.engine.find_opportunities(market_pairs)
    
    print(f"\n4️⃣ RESULTADO:")
    print(f"   • Matches encontrados: {len(matches)}")
    print(f"   • Testados: {len(market_pairs)}")
    print(f"   • Bloqueados: {blocked_count}")
    print(f"   • Oportunidades reais: {len(opportunities)}")
    
    print(f"\n📊 RAZÕES DE BLOQUEIO:")
    for reason, count in sorted(blocked_reasons.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {reason}: {count}x")
    
    print("\n" + "=" * 60)
    print("\n💡 DIAGNÓSTICO:")
    
    if blocked_count > 0:
        print("   ⚠️  PROBLEMA ENCONTRADO!")
        print("   O validator está bloqueando matches válidos.")
        print("   Possíveis causas:")
        print("   1. Validator usa EventMatcher (antigo)")
        print("   2. Monitor usa ImprovedEventMatcher (novo)")
        print("   3. Critérios de similaridade diferentes!")
        print("\n   ✅ SOLUÇÃO:")
        print("   Atualizar market_validator.py para usar ImprovedEventMatcher")
    else:
        print("   ✅ Validação OK, problema é outro (liquidez, lucro, etc)")

if __name__ == "__main__":
    asyncio.run(main())

