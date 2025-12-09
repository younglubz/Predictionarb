"""
Mostra todas as oportunidades combinatórias em detalhes
"""
import requests
from collections import Counter

print("\n" + "="*70)
print("  📊 ANÁLISE COMPLETA - OPORTUNIDADES COMBINATÓRIAS")
print("="*70 + "\n")

# Busca oportunidades
response = requests.get("http://localhost:8000/opportunities")
data = response.json()

opportunities = data.get('opportunities', [])
combinatorial = [o for o in opportunities if o.get('type') == 'combinatorial']
traditional = [o for o in opportunities if o.get('type') != 'combinatorial']

print(f"📈 RESUMO GERAL:")
print(f"   Total de oportunidades: {len(opportunities)}")
print(f"   • Combinatórias: {len(combinatorial)}")
print(f"   • Tradicionais: {len(traditional)}\n")

if not combinatorial:
    print("❌ Nenhuma oportunidade combinatória encontrada!\n")
    exit()

# Análise por estratégia
strategies = Counter(o['strategy'] for o in combinatorial)
print("📊 POR ESTRATÉGIA:")
for strategy, count in strategies.items():
    print(f"   • {strategy}: {count}")
print()

# Análise por exchange
exchanges = []
for o in combinatorial:
    for market in o.get('markets', []):
        exchanges.append(market.get('exchange', 'unknown'))
exchange_count = Counter(exchanges)
print("🏦 POR EXCHANGE:")
for exchange, count in exchange_count.items():
    print(f"   • {exchange}: {count} mercados")
print()

# Top 20 oportunidades por lucro
print("="*70)
print("  🏆 TOP 20 OPORTUNIDADES (ordenadas por lucro)")
print("="*70 + "\n")

sorted_opps = sorted(combinatorial, key=lambda x: x['profit_pct'], reverse=True)

for i, opp in enumerate(sorted_opps[:20], 1):
    print(f"#{i} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"   💰 Lucro: {opp['profit_pct']*100:.2f}%")
    print(f"   📊 Estratégia: {opp['strategy']}")
    print(f"   ✅ Confiança: {opp['confidence']*100:.0f}%")
    print(f"   📝 Explicação: {opp['explanation']}")
    print(f"   🎯 Probabilidade Total: {opp['total_probability']:.4f}")
    print(f"   📍 Mercados ({len(opp['markets'])}):")
    
    for j, market in enumerate(opp['markets'], 1):
        question = market['question'][:70]
        print(f"      {j}. [{market['exchange']}] {question}...")
        print(f"         Outcome: {market.get('outcome', 'N/A')}")
        print(f"         Price: ${market['price']:.4f}")
        print(f"         Liquidity: ${market.get('liquidity', 0):,.0f}")
    print()

# Estatísticas
print("="*70)
print("  📈 ESTATÍSTICAS")
print("="*70 + "\n")

profits = [o['profit_pct'] * 100 for o in combinatorial]
print(f"💰 LUCROS:")
print(f"   Máximo: {max(profits):.2f}%")
print(f"   Mínimo: {min(profits):.2f}%")
print(f"   Médio: {sum(profits)/len(profits):.2f}%")
print(f"   Mediana: {sorted(profits)[len(profits)//2]:.2f}%")
print()

confidences = [o['confidence'] * 100 for o in combinatorial]
print(f"✅ CONFIANÇA:")
print(f"   Máxima: {max(confidences):.0f}%")
print(f"   Mínima: {min(confidences):.0f}%")
print(f"   Média: {sum(confidences)/len(confidences):.0f}%")
print()

# Oportunidades com lucro > 10%
high_profit = [o for o in combinatorial if o['profit_pct'] > 0.10]
print(f"🎯 OPORTUNIDADES EXCELENTES (>10% lucro): {len(high_profit)}")
print()

# Oportunidades com alta confiança (>90%)
high_confidence = [o for o in combinatorial if o['confidence'] > 0.90]
print(f"⭐ OPORTUNIDADES ALTA CONFIANÇA (>90%): {len(high_confidence)}")
print()

# Oportunidades IDEAIS (lucro > 10% E confiança > 90%)
ideal = [o for o in combinatorial if o['profit_pct'] > 0.10 and o['confidence'] > 0.90]
print(f"💎 OPORTUNIDADES IDEAIS (>10% lucro E >90% confiança): {len(ideal)}")
print()

if ideal:
    print("="*70)
    print("  💎 OPORTUNIDADES IDEAIS (MELHORES)")
    print("="*70 + "\n")
    
    for i, opp in enumerate(sorted(ideal, key=lambda x: x['profit_pct'], reverse=True)[:10], 1):
        print(f"#{i} {opp['strategy']}: {opp['profit_pct']*100:.2f}% lucro")
        print(f"    {opp['explanation']}")
        print(f"    Mercados: {', '.join(m['exchange'] for m in opp['markets'])}")
        print()

print("="*70 + "\n")

