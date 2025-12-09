"""
Script para debugar por que matches não viram oportunidades
"""
import asyncio
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monitor import ArbitrageMonitor
from config import MIN_ARBITRAGE_PROFIT, MIN_LIQUIDITY

async def analyze():
    print(f'\n📊 CONFIGURAÇÕES ATUAIS:')
    print(f'   MIN_ARBITRAGE_PROFIT: {MIN_ARBITRAGE_PROFIT*100}%')
    print(f'   MIN_LIQUIDITY: ${MIN_LIQUIDITY}')
    print()
    
    monitor = ArbitrageMonitor()
    
    # Usar os mercados já carregados
    if not monitor._cached_markets:
        print('⏳ Carregando mercados...')
        await monitor.update()
    
    markets = monitor._cached_markets
    print(f'✓ {len(markets)} mercados carregados')
    print(f'✓ {len(monitor.matches)} matches encontrados')
    print()
    
    if len(monitor.matches) == 0:
        print('❌ Nenhum match encontrado ainda. Atualizando...')
        await monitor.update()
        print(f'✓ {len(monitor.matches)} matches encontrados após atualização')
    
    if len(monitor.matches) > 0:
        print(f'\n🔍 ANALISANDO PRIMEIROS 3 MATCHES:\n')
        
        for i, match in enumerate(monitor.matches[:3]):
            m1, m2 = match
            print(f'\n{"="*60}')
            print(f'MATCH #{i+1}:')
            print(f'{"="*60}')
            print(f'Market 1: {m1.question[:70]}')
            print(f'Market 2: {m2.question[:70]}')
            print(f'Exchange 1: {m1.exchange}')
            print(f'Exchange 2: {m2.exchange}')
            print(f'Price 1: {m1.price:.4f}')
            print(f'Price 2: {m2.price:.4f}')
            print(f'Volume 1: ${m1.volume:.2f}')
            print(f'Volume 2: ${m2.volume:.2f}')
            
            # Verificar equivalência
            equivalent = monitor.matcher.are_markets_equivalent(m1, m2)
            print(f'\n✓ Equivalentes: {equivalent}')
            
            if not equivalent:
                print(f'\n❌ REJEITADO: Mercados não são equivalentes!')
                
                # Mostrar detalhes da validação
                e1 = monitor.matcher.extract_entities(m1.question)
                e2 = monitor.matcher.extract_entities(m2.question)
                print(f'\nEntidades Market 1:')
                for k, v in e1.items():
                    if v:
                        print(f'  {k}: {v}')
                print(f'\nEntidades Market 2:')
                for k, v in e2.items():
                    if v:
                        print(f'  {k}: {v}')
                        
                # Verificar diferenças específicas
                print(f'\n🔍 VERIFICANDO VALIDAÇÕES:')
                
                # Anos
                years1 = set(e1.get('years', []))
                years2 = set(e2.get('years', []))
                if years1 and years2 and years1 != years2:
                    print(f'  ❌ Anos diferentes: {years1} vs {years2}')
                
                # Estados
                states1 = set(e1.get('states', []))
                states2 = set(e2.get('states', []))
                if states1 and states2 and states1 != states2:
                    print(f'  ❌ Estados diferentes: {states1} vs {states2}')
                
                # Partidos
                parties1 = set(e1.get('parties', []))
                parties2 = set(e2.get('parties', []))
                if parties1 and parties2 and parties1 != parties2:
                    print(f'  ❌ Partidos diferentes: {parties1} vs {parties2}')
                
                # Países
                countries1 = set(e1.get('countries', []))
                countries2 = set(e2.get('countries', []))
                if countries1 and countries2 and countries1 != countries2:
                    print(f'  ❌ Países diferentes: {countries1} vs {countries2}')
                
                # Question type
                qt1 = e1.get('question_type')
                qt2 = e2.get('question_type')
                if qt1 and qt2 and qt1 != qt2:
                    print(f'  ❌ Tipos de pergunta diferentes: {qt1} vs {qt2}')
                
                # Datas de expiração
                if m1.end_date and m2.end_date:
                    diff_days = abs((m1.end_date - m2.end_date).days)
                    print(f'  ⏰ Diferença de datas: {diff_days} dias')
                    if diff_days > monitor.matcher.max_date_diff_days:
                        print(f'  ❌ Diferença > {monitor.matcher.max_date_diff_days} dias')
                
            else:
                print(f'\n✓ Mercados são equivalentes!')
                
                # Calcular arbitragem
                arb = monitor.arbitrage_engine.calculate_arbitrage(m1, m2, equivalent)
                if arb:
                    print(f'\n🎉 OPORTUNIDADE ENCONTRADA!')
                    print(f'   Profit: {arb.profit_pct*100:.2f}%')
                    print(f'   Investment: ${arb.total_investment:.2f}')
                    print(f'   Expected Return: ${arb.expected_return:.2f}')
                else:
                    print(f'\n❌ REJEITADO POR ARBITRAGE ENGINE:')
                    
                    # Calcular profit manualmente
                    if m1.price > 0 and m2.price > 0:
                        # Assumindo que são mercados opostos (Yes vs No)
                        potential_profit = 1 - (m1.price + (1 - m2.price))
                        print(f'   Profit potencial: {potential_profit*100:.2f}%')
                        print(f'   Mínimo necessário: {MIN_ARBITRAGE_PROFIT*100}%')
                        
                        if potential_profit < MIN_ARBITRAGE_PROFIT:
                            print(f'   ❌ Profit muito baixo!')
                        
                        min_volume = min(m1.volume, m2.volume)
                        print(f'   Volume mínimo: ${min_volume:.2f}')
                        print(f'   Mínimo necessário: ${MIN_LIQUIDITY}')
                        
                        if min_volume < MIN_LIQUIDITY:
                            print(f'   ❌ Liquidez muito baixa!')
    
    print(f'\n{"="*60}\n')
    print(f'📊 RESUMO:')
    print(f'   Total de mercados: {len(markets)}')
    print(f'   Total de matches: {len(monitor.matches)}')
    print(f'   Total de oportunidades: {len(monitor.opportunities)}')
    print(f'\n💡 CONCLUSÃO:')
    if len(monitor.opportunities) == 0:
        print(f'   • Matches encontrados mas sem arbitragem lucrativa')
        print(f'   • Provavelmente os mercados são sobre temas similares')
        print(f'   • Mas não são exatamente equivalentes (validações críticas)')
        print(f'   • Ou o lucro/liquidez está abaixo dos mínimos')

if __name__ == '__main__':
    asyncio.run(analyze())

