# -*- coding: utf-8 -*-
"""Testa aliases de candidatos e normalizacao de estados"""
from exchanges.base import Market
from datetime import datetime
from matcher_improved import ImprovedEventMatcher


def test_aliases_and_normalization():
    """Testa se o matcher normaliza candidatos e estados corretamente"""
    
    matcher = ImprovedEventMatcher(similarity_threshold=0.60, max_date_diff_days=7)
    
    print("\n" + "="*70)
    print("TESTANDO ALIASES E NORMALIZACAO")
    print("="*70)
    
    # ========================================================================
    # TESTE 1: Aliases de Candidatos
    # ========================================================================
    print("\n\n=== TESTE 1: ALIASES DE CANDIDATOS ===\n")
    
    # 1.1 - "Biden" vs "Joe Biden" (DEVE ACEITAR)
    market_biden = Market(
        exchange="predictit",
        market_id="1",
        question="Will Biden win the 2024 presidential election?",
        outcome="Yes",
        price=0.50,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2024, 11, 5),
        url="https://example.com/1"
    )
    
    market_joe_biden = Market(
        exchange="polymarket",
        market_id="2",
        question="Will Joe Biden win the 2024 presidential election?",
        outcome="Yes",
        price=0.49,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2024, 11, 5),
        url="https://example.com/2"
    )
    
    is_match, similarity, details = matcher.are_markets_equivalent(
        market_biden, 
        market_joe_biden
    )
    
    print("1.1 - 'Biden' vs 'Joe Biden':")
    print(f"   Q1: {market_biden.question}")
    print(f"   Q2: {market_joe_biden.question}")
    print(f"   Candidatos 1 (normalizados): {details.get('entities1', {}).get('candidates')}")
    print(f"   Candidatos 2 (normalizados): {details.get('entities2', {}).get('candidates')}")
    print(f"   Match: {is_match} (DEVE SER TRUE)")
    
    if is_match:
        print("   PASSOU - Reconheceu Biden = Joe Biden")
    else:
        print(f"   FALHOU - Nao reconheceu alias! Razao: {details.get('reason')}")
    
    # 1.2 - "Kamala Harris" vs "Harris" (DEVE ACEITAR)
    market_kamala = Market(
        exchange="predictit",
        market_id="3",
        question="Will Kamala Harris win the 2028 Democratic nomination?",
        outcome="Yes",
        price=0.40,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2028, 7, 15),
        url="https://example.com/3"
    )
    
    market_harris = Market(
        exchange="manifold",
        market_id="4",
        question="Will Harris win the 2028 Democratic nomination?",
        outcome="Yes",
        price=0.38,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2028, 7, 15),
        url="https://example.com/4"
    )
    
    is_match2, similarity2, details2 = matcher.are_markets_equivalent(
        market_kamala,
        market_harris
    )
    
    print("\n1.2 - 'Kamala Harris' vs 'Harris':")
    print(f"   Candidatos 1: {details2.get('entities1', {}).get('candidates')}")
    print(f"   Candidatos 2: {details2.get('entities2', {}).get('candidates')}")
    print(f"   Match: {is_match2} (DEVE SER TRUE)")
    
    if is_match2:
        print("   PASSOU - Reconheceu Kamala Harris = Harris")
    else:
        print(f"   FALHOU - Razao: {details2.get('reason')}")
    
    # 1.3 - "Trump" vs "Donald Trump" (DEVE ACEITAR)
    market_trump = Market(
        exchange="polymarket",
        market_id="5",
        question="Will Trump win the 2028 Republican nomination?",
        outcome="Yes",
        price=0.55,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2028, 7, 20),
        url="https://example.com/5"
    )
    
    market_donald = Market(
        exchange="predictit",
        market_id="6",
        question="Will Donald Trump win the 2028 Republican nomination?",
        outcome="Yes",
        price=0.53,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2028, 7, 20),
        url="https://example.com/6"
    )
    
    is_match3, similarity3, details3 = matcher.are_markets_equivalent(
        market_trump,
        market_donald
    )
    
    print("\n1.3 - 'Trump' vs 'Donald Trump':")
    print(f"   Candidatos 1: {details3.get('entities1', {}).get('candidates')}")
    print(f"   Candidatos 2: {details3.get('entities2', {}).get('candidates')}")
    print(f"   Match: {is_match3} (DEVE SER TRUE)")
    
    if is_match3:
        print("   PASSOU - Reconheceu Trump = Donald Trump")
    else:
        print(f"   FALHOU - Razao: {details3.get('reason')}")
    
    # ========================================================================
    # TESTE 2: Normalizacao de Estados
    # ========================================================================
    print("\n\n=== TESTE 2: NORMALIZACAO DE ESTADOS ===\n")
    
    # 2.1 - "TX" vs "Texas" (DEVE ACEITAR)
    market_tx = Market(
        exchange="predictit",
        market_id="7",
        question="Who will win the TX Senate race in 2026?",
        outcome="Yes",
        price=0.50,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2026, 11, 3),
        url="https://example.com/7"
    )
    
    market_texas = Market(
        exchange="polymarket",
        market_id="8",
        question="Who will win the Texas Senate race in 2026?",
        outcome="Yes",
        price=0.48,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2026, 11, 3),
        url="https://example.com/8"
    )
    
    is_match4, similarity4, details4 = matcher.are_markets_equivalent(
        market_tx,
        market_texas
    )
    
    print("2.1 - 'TX' vs 'Texas':")
    print(f"   Estados 1 (normalizados): {details4.get('entities1', {}).get('states')}")
    print(f"   Estados 2 (normalizados): {details4.get('entities2', {}).get('states')}")
    print(f"   Match: {is_match4} (DEVE SER TRUE)")
    
    if is_match4:
        print("   PASSOU - Reconheceu TX = Texas")
    else:
        print(f"   FALHOU - Razao: {details4.get('reason')}")
    
    # 2.2 - "NY" vs "New York" (DEVE ACEITAR)
    market_ny = Market(
        exchange="manifold",
        market_id="9",
        question="Who will win the NY gubernatorial race?",
        outcome="Yes",
        price=0.60,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2026, 11, 3),
        url="https://example.com/9"
    )
    
    market_newyork = Market(
        exchange="predictit",
        market_id="10",
        question="Who will win the New York gubernatorial race?",
        outcome="Yes",
        price=0.58,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2026, 11, 3),
        url="https://example.com/10"
    )
    
    is_match5, similarity5, details5 = matcher.are_markets_equivalent(
        market_ny,
        market_newyork
    )
    
    print("\n2.2 - 'NY' vs 'New York':")
    print(f"   Estados 1: {details5.get('entities1', {}).get('states')}")
    print(f"   Estados 2: {details5.get('entities2', {}).get('states')}")
    print(f"   Match: {is_match5} (DEVE SER TRUE)")
    
    if is_match5:
        print("   PASSOU - Reconheceu NY = New York")
    else:
        print(f"   FALHOU - Razao: {details5.get('reason')}")
    
    # 2.3 - "CA" vs "California" (DEVE ACEITAR)
    market_ca = Market(
        exchange="polymarket",
        market_id="11",
        question="CA Senate Democratic primary winner 2026",
        outcome="Yes",
        price=0.45,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2026, 3, 3),
        url="https://example.com/11"
    )
    
    market_calif = Market(
        exchange="predictit",
        market_id="12",
        question="California Senate Democratic primary winner 2026",
        outcome="Yes",
        price=0.43,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2026, 3, 3),
        url="https://example.com/12"
    )
    
    is_match6, similarity6, details6 = matcher.are_markets_equivalent(
        market_ca,
        market_calif
    )
    
    print("\n2.3 - 'CA' vs 'California':")
    print(f"   Estados 1: {details6.get('entities1', {}).get('states')}")
    print(f"   Estados 2: {details6.get('entities2', {}).get('states')}")
    print(f"   Match: {is_match6} (DEVE SER TRUE)")
    
    if is_match6:
        print("   PASSOU - Reconheceu CA = California")
    else:
        print(f"   FALHOU - Razao: {details6.get('reason')}")
    
    # ========================================================================
    # RESUMO
    # ========================================================================
    print("\n\n" + "="*70)
    print("RESUMO DOS TESTES")
    print("="*70)
    
    tests = [
        ("Alias - Biden = Joe Biden", is_match),
        ("Alias - Kamala Harris = Harris", is_match2),
        ("Alias - Trump = Donald Trump", is_match3),
        ("Estado - TX = Texas", is_match4),
        ("Estado - NY = New York", is_match5),
        ("Estado - CA = California", is_match6),
    ]
    
    for name, passed in tests:
        status = "PASSOU" if passed else "FALHOU"
        print(f"  {status:6} - {name}")
    
    total_passed = sum(1 for _, p in tests if p)
    print(f"\nTotal: {total_passed}/6 testes passaram")
    
    if total_passed == 6:
        print("\nSUCESSO - Aliases e normalizacao funcionando perfeitamente!")
    else:
        print(f"\nFALHOU - {6-total_passed} teste(s) falharam")


if __name__ == "__main__":
    test_aliases_and_normalization()

