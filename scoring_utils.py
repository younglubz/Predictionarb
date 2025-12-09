"""
Utilitários para cálculo de scores e riscos de oportunidades de arbitragem

Fornece funções consistentes para calcular:
- quality_score: Score de qualidade geral (0-100)
- risk_score: Score de risco (0-1, onde 0 = baixo risco, 1 = alto risco)
- liquidity_score: Score de liquidez (0-1)
"""
from typing import List
from exchanges.base import Market
from datetime import datetime


def calculate_liquidity_score(markets: List[Market]) -> float:
    """
    Calcula score de liquidez (0-1)
    
    Baseado em:
    - Liquidez mínima entre os mercados
    - Volume 24h
    - Número de mercados (mais mercados = mais complexo)
    """
    if not markets:
        return 0.0
    
    min_liquidity = min(m.liquidity for m in markets if m.liquidity)
    total_volume = sum(m.volume_24h or 0 for m in markets)
    avg_liquidity = sum(m.liquidity for m in markets if m.liquidity) / len(markets)
    
    # Normaliza baseado em thresholds
    liquidity_score = 0.0
    
    # Baseado em liquidez mínima (peso 50%)
    if min_liquidity > 100000:
        liquidity_score += 0.5
    elif min_liquidity > 50000:
        liquidity_score += 0.4
    elif min_liquidity > 10000:
        liquidity_score += 0.3
    elif min_liquidity > 5000:
        liquidity_score += 0.2
    elif min_liquidity > 1000:
        liquidity_score += 0.1
    
    # Baseado em volume 24h (peso 30%)
    if total_volume > 100000:
        liquidity_score += 0.3
    elif total_volume > 50000:
        liquidity_score += 0.25
    elif total_volume > 10000:
        liquidity_score += 0.2
    elif total_volume > 5000:
        liquidity_score += 0.15
    elif total_volume > 1000:
        liquidity_score += 0.1
    
    # Baseado em liquidez média (peso 20%)
    if avg_liquidity > 50000:
        liquidity_score += 0.2
    elif avg_liquidity > 20000:
        liquidity_score += 0.15
    elif avg_liquidity > 10000:
        liquidity_score += 0.1
    elif avg_liquidity > 5000:
        liquidity_score += 0.05
    
    return min(liquidity_score, 1.0)


def calculate_risk_score(
    markets: List[Market],
    profit_pct: float,
    confidence: float,
    strategy: str = "",
    time_to_expiry_hours: float = None
) -> float:
    """
    Calcula score de risco (0-1, onde 0 = baixo risco, 1 = alto risco)
    
    Fatores de risco:
    - Baixa liquidez (30%)
    - Múltiplas exchanges (20%)
    - Estratégia de venda (15%)
    - Lucro suspeito (15%)
    - Tempo até expiração (10%)
    - Baixa confiança no matching (10%)
    """
    risk = 0.0
    
    # 1. Risco de liquidez (30%)
    liquidity_score = calculate_liquidity_score(markets)
    risk += (1 - liquidity_score) * 0.3
    
    # 2. Risco de execução - múltiplas exchanges (20%)
    exchanges = set(m.exchange for m in markets)
    if len(exchanges) > 1:
        risk += 0.2  # Executar em múltiplas exchanges aumenta risco
    
    # 3. Risco de estratégia (15%)
    if "sell" in strategy.lower() or "vender" in strategy.lower():
        risk += 0.15  # Venda requer margem
    
    # 4. Lucro suspeito - muito alto pode ser erro (15%)
    if profit_pct > 1.0:  # >100% lucro
        risk += 0.15
    elif profit_pct > 0.5:  # >50% lucro
        risk += 0.1
    elif profit_pct > 0.3:  # >30% lucro
        risk += 0.05
    
    # 5. Tempo até expiração (10%)
    if time_to_expiry_hours is not None:
        if time_to_expiry_hours < 1:  # Menos de 1 hora
            risk += 0.1
        elif time_to_expiry_hours < 6:  # Menos de 6 horas
            risk += 0.05
        elif time_to_expiry_hours < 24:  # Menos de 24 horas
            risk += 0.02
    else:
        # Calcula baseado em expires_at dos mercados
        now = datetime.now()
        for market in markets:
            if market.expires_at:
                try:
                    expiry = market.expires_at
                    if expiry.tzinfo and now.tzinfo is None:
                        from datetime import timezone
                        now = datetime.now(timezone.utc)
                    elif expiry.tzinfo is None and now.tzinfo:
                        expiry = expiry.replace(tzinfo=now.tzinfo)
                    
                    hours_to_expiry = (expiry - now).total_seconds() / 3600
                    if hours_to_expiry < 1:
                        risk += 0.05
                        break
                    elif hours_to_expiry < 6:
                        risk += 0.03
                        break
                    elif hours_to_expiry < 24:
                        risk += 0.01
                        break
                except Exception:
                    pass
    
    # 6. Baixa confiança no matching (10%)
    if confidence < 0.5:
        risk += 0.1
    elif confidence < 0.7:
        risk += 0.05
    elif confidence < 0.8:
        risk += 0.02
    
    return min(risk, 1.0)


def calculate_quality_score(
    profit_pct: float,
    confidence: float,
    liquidity_score: float,
    risk_score: float,
    spread_pct: float = None,
    volatility_score: float = None
) -> float:
    """
    Calcula score de qualidade geral (0-100)
    
    Fatores:
    - Lucro líquido (35%)
    - Confiança no matching (25%)
    - Liquidez (20%)
    - Segurança (baixo risco) (15%)
    - Spread/Volatilidade (5% - bonus)
    """
    score = 0.0
    
    # 1. Lucro líquido (35 pontos máximos)
    profit_score = min(profit_pct * 100, 50)  # Cap em 50% para evitar distorção
    score += (profit_score / 50) * 35
    
    # 2. Confiança no matching (25 pontos máximos)
    score += confidence * 25
    
    # 3. Liquidez (20 pontos máximos)
    score += liquidity_score * 20
    
    # 4. Segurança - baixo risco (15 pontos máximos)
    safety_score = 1.0 - risk_score
    score += safety_score * 15
    
    # 5. Spread/Volatilidade (5 pontos máximos - bonus)
    if spread_pct is not None:
        # Spread ideal entre 2-15%
        if 0.02 <= spread_pct <= 0.15:
            score += 5
        elif 0.15 < spread_pct <= 0.30:
            score += 3
        elif spread_pct > 0.30:
            score += 1  # Spread muito grande pode ser suspeito
    
    if volatility_score is not None:
        # Volatilidade moderada é boa (0.3-0.7)
        if 0.3 <= volatility_score <= 0.7:
            score += 2
    
    return min(score, 100.0)


def get_risk_level(risk_score: float) -> str:
    """
    Converte risk_score numérico (0-1) para nível textual
    
    Args:
        risk_score: Score de risco de 0-1
        
    Returns:
        "baixo", "médio", ou "alto"
    """
    if risk_score < 0.3:
        return "baixo"
    elif risk_score < 0.6:
        return "médio"
    else:
        return "alto"


def get_quality_rating(quality_score: float) -> str:
    """
    Converte quality_score (0-100) para classificação textual
    
    Args:
        quality_score: Score de qualidade de 0-100
        
    Returns:
        "excelente", "bom", "médio", "baixo"
    """
    if quality_score >= 80:
        return "excelente"
    elif quality_score >= 60:
        return "bom"
    elif quality_score >= 40:
        return "médio"
    else:
        return "baixo"

