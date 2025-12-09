# -*- coding: utf-8 -*-
"""Testa validacao de paises"""
from exchanges.base import Market
from datetime import datetime
from matcher_improved import ImprovedEventMatcher


def test_country_validation():
    """Testa se o matcher detecta corretamente paises diferentes"""
    
    matcher = ImprovedEventMatcher(similarity_threshold=0.60)
    
    # Teste 1: US vs Turkey (DEVE SER REJEITADO)
    us_market = Market(
        exchange="predictit",
        market_id="1",
        question="Who will win the 2028 US presidential election?",
        outcome="Yes",
        price=0.50,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2028, 11, 5),
        url="https://example.com/1"
    )
    
    turkey_market = Market(
        exchange="kalshi",
        market_id="2",
        question="Who will win the next Turkish presidential election?",
        outcome="Yes",
        price=0.55,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2028, 6, 1),
        url="https://example.com/2"
    )
    
    is_match, similarity, details = matcher.are_markets_equivalent(us_market, turkey_market)
    
    print("\n=== TESTE 1: US vs Turkey ===")
    print(f"Questao 1: {us_market.question}")
    print(f"Questao 2: {turkey_market.question}")
    print(f"\nEntidades US: {details.get('entities1', {})}")
    print(f"Entidades Turkey: {details.get('entities2', {})}")
    print(f"\nMatch: {is_match} (DEVE SER FALSE)")
    print(f"Razao: {details.get('reason', 'N/A')}")
    
    if not is_match and details.get('reason') == 'different_countries':
        print("PASSOU - Corretamente rejeitou paises diferentes!")
    else:
        print("FALHOU - Nao detectou paises diferentes!")
    
    # Teste 2: Texas Senate (mesmo pais) (DEVE SER ACEITO)
    predictit_texas = Market(
        exchange="predictit",
        market_id="8180",
        question="Who will win the 2026 Texas Democratic Senate nomination",
        outcome="Yes",
        price=0.50,
        volume_24h=5000,
        liquidity=10000,
        expires_at=datetime(2026, 3, 3),
        url="https://example.com/3"
    )
    
    polymarket_texas = Market(
        exchange="polymarket",
        market_id="texas-dem",
        question="Texas Democratic Senate Primary Winner",
        outcome="Yes",
        price=0.49,
        volume_24h=9302,
        liquidity=15000,
        expires_at=datetime(2026, 3, 3),
        url="https://example.com/4"
    )
    
    is_match2, similarity2, details2 = matcher.are_markets_equivalent(
        predictit_texas, 
        polymarket_texas
    )
    
    print("\n\n=== TESTE 2: Texas Senate (Mesmo Pais) ===")
    print(f"Questao 1: {predictit_texas.question}")
    print(f"Questao 2: {polymarket_texas.question}")
    print(f"\nEntidades 1: {details2.get('entities1', {})}")
    print(f"Entidades 2: {details2.get('entities2', {})}")
    print(f"\nMatch: {is_match2} (DEVE SER TRUE)")
    print(f"Similaridade: {similarity2:.2%}")
    
    if is_match2:
        print("PASSOU - Corretamente aceitou mesmo pais!")
    else:
        print(f"FALHOU - Rejeitou incorretamente! Razao: {details2.get('reason', 'N/A')}")
    
    # Teste 3: UK vs US (DEVE SER REJEITADO)
    uk_market = Market(
        exchange="manifold",
        market_id="uk1",
        question="Who will be the next UK Prime Minister?",
        outcome="Yes",
        price=0.45,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2025, 12, 31),
        url="https://example.com/5"
    )
    
    us_pm_market = Market(
        exchange="predictit",
        market_id="us1",
        question="Who will be the next US President?",
        outcome="Yes",
        price=0.48,
        volume_24h=1000,
        liquidity=5000,
        expires_at=datetime(2028, 11, 5),
        url="https://example.com/6"
    )
    
    is_match3, similarity3, details3 = matcher.are_markets_equivalent(uk_market, us_pm_market)
    
    print("\n\n=== TESTE 3: UK vs US ===")
    print(f"Questao 1: {uk_market.question}")
    print(f"Questao 2: {us_pm_market.question}")
    print(f"\nEntidades UK: {details3.get('entities1', {})}")
    print(f"Entidades US: {details3.get('entities2', {})}")
    print(f"\nMatch: {is_match3} (DEVE SER FALSE)")
    print(f"Razao: {details3.get('reason', 'N/A')}")
    
    if not is_match3 and details3.get('reason') == 'different_countries':
        print("PASSOU - Corretamente rejeitou paises diferentes!")
    else:
        print("FALHOU - Nao detectou paises diferentes!")
    
    # Resumo
    print("\n\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    
    test1_pass = not is_match and details.get('reason') == 'different_countries'
    test2_pass = is_match2
    test3_pass = not is_match3 and details3.get('reason') == 'different_countries'
    
    total_pass = sum([test1_pass, test2_pass, test3_pass])
    
    print(f"\nTeste 1 (US vs Turkey): {'PASSOU' if test1_pass else 'FALHOU'}")
    print(f"Teste 2 (Texas Senate): {'PASSOU' if test2_pass else 'FALHOU'}")
    print(f"Teste 3 (UK vs US): {'PASSOU' if test3_pass else 'FALHOU'}")
    print(f"\nTotal: {total_pass}/3 testes passaram")
    
    if total_pass == 3:
        print("\nSUCESSO - Validacao de paises funcionando perfeitamente!")
    else:
        print("\nFALHOU - Alguns testes nao passaram")


if __name__ == "__main__":
    test_country_validation()

