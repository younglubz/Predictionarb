"""
Verifica oportunidade de arbitragem entre Polymarket e Kalshi
para TIME Person of the Year 2025
"""

# Dados do Polymarket (do link fornecido)
polymarket = {
    "Artificial Intelligence": {"yes": 0.45, "no": 0.56, "volume": 2536692},
    "Jensen Huang": {"yes": 0.21, "no": 0.81, "volume": 1413853},
    "Sam Altman": {"yes": 0.14, "no": 0.88, "volume": 872825},
    "Pope Leo XIV": {"yes": 0.07, "no": 0.94, "volume": 2317400},
    "Donald Trump": {"yes": 0.036, "no": 0.966, "volume": 3626800},
    "Benjamin Netanyahu": {"yes": 0.027, "no": 0.976, "volume": 2121045},
    "Elon Musk": {"yes": 0.008, "no": 0.994, "volume": 1250428},
}

# Taxas
polymarket_fee = 0.02  # 2%
kalshi_fee = 0.07      # 7%

print("\n" + "="*70)
print("  🔍 ANÁLISE DE ARBITRAGEM - TIME PERSON OF THE YEAR 2025")
print("="*70 + "\n")

print("📊 POLYMARKET (dados disponíveis):")
for candidate, data in polymarket.items():
    print(f"   • {candidate:25s}: Yes={data['yes']:.3f} No={data['no']:.3f} Vol=${data['volume']:,.0f}")

print("\n" + "="*70)
print("  💡 TIPOS DE ARBITRAGEM POSSÍVEIS")
print("="*70 + "\n")

# 1. Verificar mercados complementares (Yes + No != 1.0)
print("1️⃣  ARBITRAGEM DE REBALANCEAMENTO (Yes + No != 1.0):")
print("    Explorar quando P(Yes) + P(No) ≠ 1.0 no mesmo mercado\n")

rebalancing_opps = []
for candidate, data in polymarket.items():
    total = data['yes'] + data['no']
    if abs(total - 1.0) > 0.01:  # Diferença > 1%
        profit = abs(total - 1.0)
        profit_pct = (profit / min(data['yes'], data['no'])) * 100 if min(data['yes'], data['no']) > 0 else 0
        
        # Após taxas
        net_profit = profit - (polymarket_fee * 2)  # Taxa em ambos os lados
        
        if total > 1.0:
            strategy = "VENDER ambos (Yes + No)"
            explanation = f"Custo: ${total:.3f}, Retorno: $1.00, Lucro bruto: ${profit:.3f}"
        else:
            strategy = "COMPRAR ambos (Yes + No)"
            explanation = f"Custo: ${total:.3f}, Retorno: $1.00, Lucro bruto: ${profit:.3f}"
        
        rebalancing_opps.append({
            'candidate': candidate,
            'strategy': strategy,
            'total': total,
            'profit': profit,
            'profit_pct': profit_pct,
            'net_profit': net_profit,
            'explanation': explanation
        })
        
        if net_profit > 0:
            print(f"    ✅ {candidate}")
            print(f"       {strategy}")
            print(f"       {explanation}")
            print(f"       Lucro após taxas: ${net_profit:.4f} ({(net_profit/total)*100:.2f}%)")
            print(f"       Volume disponível: ${data['volume']:,.0f}\n")
        else:
            print(f"    ❌ {candidate}")
            print(f"       {strategy}")
            print(f"       Lucro bruto: ${profit:.4f}, mas taxas (4%) eliminam o lucro")
            print(f"       Lucro líquido: ${net_profit:.4f} (negativo)\n")

print("\n" + "="*70)
print("  📈 RESUMO")
print("="*70 + "\n")

viable_opps = [o for o in rebalancing_opps if o['net_profit'] > 0]

if viable_opps:
    print(f"✅ ENCONTRADAS {len(viable_opps)} OPORTUNIDADES VIÁVEIS!\n")
    
    # Ordenar por lucro líquido
    viable_opps.sort(key=lambda x: x['net_profit'], reverse=True)
    
    print("🏆 TOP OPORTUNIDADES:\n")
    for i, opp in enumerate(viable_opps[:5], 1):
        print(f"{i}. {opp['candidate']}")
        print(f"   Lucro líquido: ${opp['net_profit']:.4f} ({(opp['net_profit']/opp['total'])*100:.2f}%)")
        print(f"   {opp['strategy']}")
        print(f"   {opp['explanation']}\n")
else:
    print("❌ NENHUMA OPORTUNIDADE VIÁVEL ENCONTRADA\n")
    print("🔍 MOTIVO:")
    print("   As taxas da Polymarket (2% por operação = 4% total) eliminam")
    print("   o lucro potencial das pequenas discrepâncias de preço.\n")
    
    if rebalancing_opps:
        best_gross = max(rebalancing_opps, key=lambda x: x['profit'])
        print(f"   Melhor oportunidade bruta: {best_gross['candidate']}")
        print(f"   Lucro bruto: ${best_gross['profit']:.4f} ({best_gross['profit_pct']:.2f}%)")
        print(f"   Mas após taxas: ${best_gross['net_profit']:.4f} (negativo)\n")

print("\n" + "="*70)
print("  ⚠️  NOTA IMPORTANTE")
print("="*70 + "\n")

print("Para arbitragem entre Polymarket e Kalshi, precisamos dos preços")
print("da Kalshi. O link fornecido não mostrou os preços específicos.")
print("\nSe Kalshi tiver preços MUITO diferentes para os mesmos candidatos,")
print("pode haver arbitragem tradicional (comprar em uma, vender na outra).\n")
print("Mas as taxas combinadas (Polymarket 2% + Kalshi 7% = 9%) exigem")
print("uma diferença de preço > 9% para ser lucrativo.\n")

print("="*70 + "\n")

