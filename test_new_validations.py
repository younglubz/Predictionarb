# -*- coding: utf-8 -*-
"""Testa as novas validacoes: candidatos, datas, tipo de questao"""
from exchanges.base import Market
from datetime import datetime, timedelta
from matcher_improved import ImprovedEventMatcher


def test_new_validations():
    """Testa as 3 novas validacoes"""
    
    matcher = ImprovedEventMatcher(similarity_threshold=0.60, max_date_diff_days=7)
    
    print("\n" + "="*70)
    print("TESTANDO NOVAS VALIDACOES")
    print("="*70)
    
    # ========================================================================
    # TESTE 1: Validacao de DATA DE EXPIRACAO
    # ========================================================================
    print("\n\n=== TESTE 1: VALIDACAO DE DATA DE EXPIRACAO ===\n")
    
    # 1.1 - Mesma data (DEVE ACEITAR)
    market_date1 = Market(
        exchange="predictit",
        market_id="1",
        question="Who will win the 2026 Texas Senate race?",
        outcome="Yes",
        price=0.50,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2026, 11, 3),
        url="https://example.com/1"
    )
    
    market_date2 = Market(
        exchange="polymarket",
        market_id="2",
        question="Texas Senate race winner 2026",
        outcome="Yes",
        price=0.48,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2026, 11, 3),  # MESMA DATA
        url="https://example.com/2"
    )
    
    is_match, similarity, details = matcher.are_markets_equivalent(market_date1, market_date2)
    
    print("1.1 - Mesma data (3 Nov 2026):")
    print(f"   Match: {is_match} (DEVE SER TRUE)")
    if is_match:
        print("   PASSOU - Aceitou mesma data")
    else:
        print(f"   FALHOU - Rejeitou mesma data! Razao: {details.get('reason')}")
    
    # 1.2 - Datas muito diferentes (DEVE REJEITAR)
    market_date3 = Market(
        exchange="manifold",
        market_id="3",
        question="Texas Senate race winner 2026",
        outcome="Yes",
        price=0.49,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2027, 1, 15),  # 2 meses depois!
        url="https://example.com/3"
    )
    
    is_match2, similarity2, details2 = matcher.are_markets_equivalent(market_date1, market_date3)
    
    print("\n1.2 - Datas muito diferentes (Nov 2026 vs Jan 2027):")
    print(f"   Match: {is_match2} (DEVE SER FALSE)")
    print(f"   Razao: {details2.get('reason')}")
    print(f"   Diferenca: {details2.get('date_diff_days')} dias")
    if not is_match2 and details2.get('reason') == 'different_expiration_dates':
        print("   PASSOU - Rejeitou datas diferentes")
    else:
        print("   FALHOU - Nao rejeitou datas diferentes")
    
    # ========================================================================
    # TESTE 2: Validacao de TIPO DE QUESTAO
    # ========================================================================
    print("\n\n=== TESTE 2: VALIDACAO DE TIPO DE QUESTAO ===\n")
    
    # 2.1 - "Who will win" vs "Who will win" (DEVE ACEITAR)
    market_who1 = Market(
        exchange="predictit",
        market_id="4",
        question="Who will win the 2028 presidential election?",
        outcome="Yes",
        price=0.50,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2028, 11, 5),
        url="https://example.com/4"
    )
    
    market_who2 = Market(
        exchange="polymarket",
        market_id="5",
        question="2028 Presidential election winner",
        outcome="Yes",
        price=0.48,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2028, 11, 5),
        url="https://example.com/5"
    )
    
    is_match3, similarity3, details3 = matcher.are_markets_equivalent(market_who1, market_who2)
    
    print("2.1 - Ambos 'Who will win' (perguntas abertas):")
    print(f"   Q1 tipo: {details3.get('entities1', {}).get('question_type')}")
    print(f"   Q2 tipo: {details3.get('entities2', {}).get('question_type')}")
    print(f"   Match: {is_match3} (DEVE SER TRUE)")
    if is_match3:
        print("   PASSOU - Aceitou mesmo tipo de questao")
    else:
        print(f"   FALHOU - Rejeitou! Razao: {details3.get('reason')}")
    
    # 2.2 - "Who will win" vs "Will Biden win" (DEVE REJEITAR)
    market_biden = Market(
        exchange="manifold",
        market_id="6",
        question="Will Biden win the 2028 presidential election?",
        outcome="Yes",
        price=0.30,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2028, 11, 5),
        url="https://example.com/6"
    )
    
    is_match4, similarity4, details4 = matcher.are_markets_equivalent(market_who1, market_biden)
    
    print("\n2.2 - 'Who will win' vs 'Will Biden win':")
    print(f"   Q1: {market_who1.question[:50]}")
    print(f"   Q1 tipo: {details4.get('entities1', {}).get('question_type')}")
    print(f"   Q2: {market_biden.question[:50]}")
    print(f"   Q2 tipo: {details4.get('entities2', {}).get('question_type')}")
    print(f"   Match: {is_match4} (DEVE SER FALSE)")
    print(f"   Razao: {details4.get('reason')}")
    if not is_match4 and 'question_type' in details4.get('reason', ''):
        print("   PASSOU - Rejeitou tipos diferentes")
    else:
        print("   FALHOU - Nao rejeitou tipos diferentes")
    
    # ========================================================================
    # TESTE 3: Validacao de CANDIDATOS ESPECIFICOS
    # ========================================================================
    print("\n\n=== TESTE 3: VALIDACAO DE CANDIDATOS ESPECIFICOS ===\n")
    
    # 3.1 - Mesmo candidato (DEVE ACEITAR)
    market_harris1 = Market(
        exchange="predictit",
        market_id="7",
        question="Will Kamala Harris win the 2028 Democratic nomination?",
        outcome="Yes",
        price=0.35,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2028, 7, 15),
        url="https://example.com/7"
    )
    
    market_harris2 = Market(
        exchange="polymarket",
        market_id="8",
        question="Kamala Harris to win 2028 Democratic primary",
        outcome="Yes",
        price=0.33,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2028, 7, 18),  # 3 dias de diferenca (OK)
        url="https://example.com/8"
    )
    
    is_match5, similarity5, details5 = matcher.are_markets_equivalent(market_harris1, market_harris2)
    
    print("3.1 - Mesmo candidato (Kamala Harris):")
    print(f"   Candidatos 1: {details5.get('entities1', {}).get('candidates')}")
    print(f"   Candidatos 2: {details5.get('entities2', {}).get('candidates')}")
    print(f"   Match: {is_match5} (DEVE SER TRUE)")
    if is_match5:
        print("   PASSOU - Aceitou mesmo candidato")
    else:
        print(f"   FALHOU - Rejeitou mesmo candidato! Razao: {details5.get('reason')}")
    
    # 3.2 - Candidatos diferentes (DEVE REJEITAR)
    market_newsom = Market(
        exchange="manifold",
        market_id="9",
        question="Will Gavin Newsom win the 2028 Democratic nomination?",
        outcome="Yes",
        price=0.40,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2028, 7, 15),
        url="https://example.com/9"
    )
    
    is_match6, similarity6, details6 = matcher.are_markets_equivalent(market_harris1, market_newsom)
    
    print("\n3.2 - Candidatos diferentes (Harris vs Newsom):")
    print(f"   Candidatos 1: {details6.get('entities1', {}).get('candidates')}")
    print(f"   Candidatos 2: {details6.get('entities2', {}).get('candidates')}")
    print(f"   Match: {is_match6} (DEVE SER FALSE)")
    print(f"   Razao: {details6.get('reason')}")
    if not is_match6 and 'candidates' in details6.get('reason', ''):
        print("   PASSOU - Rejeitou candidatos diferentes")
    else:
        print("   FALHOU - Nao rejeitou candidatos diferentes")
    
    # ========================================================================
    # RESUMO
    # ========================================================================
    print("\n\n" + "="*70)
    print("RESUMO DOS TESTES")
    print("="*70)
    
    test1_1 = is_match
    test1_2 = not is_match2 and details2.get('reason') == 'different_expiration_dates'
    test2_1 = is_match3
    test2_2 = not is_match4
    test3_1 = is_match5
    test3_2 = not is_match6
    
    tests = [
        ("Data - Mesma data", test1_1),
        ("Data - Datas diferentes", test1_2),
        ("Tipo - Ambos 'who will win'", test2_1),
        ("Tipo - Tipos diferentes", test2_2),
        ("Candidato - Mesmo candidato", test3_1),
        ("Candidato - Candidatos diferentes", test3_2),
    ]
    
    for name, passed in tests:
        status = "PASSOU" if passed else "FALHOU"
        color = "green" if passed else "red"
        print(f"  {status:6} - {name}")
    
    total_passed = sum(1 for _, p in tests if p)
    print(f"\nTotal: {total_passed}/6 testes passaram")
    
    if total_passed == 6:
        print("\nSUCESSO - Todas as validacoes funcionando!")
    else:
        print(f"\nFALHOU - {6-total_passed} teste(s) falharam")


if __name__ == "__main__":
    test_new_validations()

