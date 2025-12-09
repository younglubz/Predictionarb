"""
Arbitragem por Probabilidade - Compara % entre exchanges

Este módulo identifica oportunidades de arbitragem comparando as probabilidades
(percentuais) de mercados equivalentes entre diferentes exchanges.

Exemplo:
- Kalshi: "Biden wins 2024" = 60% ($0.60)
- PredictIt: "Biden wins 2024" = 65% ($0.65)
- Oportunidade: Comprar em Kalshi (60%) e vender em PredictIt (65%) = 5% lucro
"""
from typing import List, Optional, Tuple
from exchanges.base import Market
from dataclasses import dataclass, field
from config import MIN_ARBITRAGE_PROFIT, MIN_LIQUIDITY, EXCHANGE_FEES, GAS_FEES
from matcher_improved import ImprovedEventMatcher
from scoring_utils import calculate_liquidity_score, calculate_risk_score, calculate_quality_score, get_risk_level


@dataclass
class ProbabilityArbitrageOpportunity:
    """Oportunidade de arbitragem baseada em probabilidade"""
    market_low: Market      # Exchange com probabilidade menor (comprar aqui)
    market_high: Market     # Exchange com probabilidade maior (vender aqui)
    probability_low: float  # Probabilidade menor (ex: 0.60 = 60%)
    probability_high: float # Probabilidade maior (ex: 0.65 = 65%)
    spread_pct: float       # Diferença percentual (ex: 5% = 0.05)
    profit_pct: float       # Lucro percentual após taxas
    profit_abs: float       # Lucro absoluto (assumindo $100)
    fees: float
    net_profit: float
    confidence: float       # Confiança no matching (0-1)
    explanation: str
    risk_score: float = field(default=0.0)  # Score numérico de risco (0-1)
    liquidity_score: float = field(default=0.0)  # Score de liquidez (0-1)
    quality_score: float = field(default=0.0)  # Score de qualidade (0-100)
    risk_level: str = field(default="médio")  # Nível de risco textual
    
    def __str__(self):
        return (
            f"Arbitragem por Probabilidade: {self.profit_pct:.2%} lucro\n"
            f"  Spread: {self.spread_pct:.2%} ({self.probability_low:.1%} vs {self.probability_high:.1%})\n"
            f"  Comprar: {self.market_low.exchange} @ {self.probability_low:.1%}\n"
            f"  Vender: {self.market_high.exchange} @ {self.probability_high:.1%}\n"
            f"  Lucro líquido: ${self.net_profit:.2f} (${100} investido)\n"
            f"  Confiança: {self.confidence:.1%}"
        )


class ProbabilityArbitrageEngine:
    """
    Detecta oportunidades de arbitragem comparando probabilidades entre exchanges
    
    Estratégia:
    1. Encontra mercados equivalentes entre exchanges diferentes
    2. Compara as probabilidades (preços) de cada mercado
    3. Identifica spreads significativos que permitam arbitragem
    4. Calcula lucro líquido considerando taxas
    """
    
    def __init__(self, matcher: ImprovedEventMatcher):
        self.matcher = matcher
        self.min_profit = MIN_ARBITRAGE_PROFIT
        self.min_liquidity = MIN_LIQUIDITY
        self.min_spread = 0.02  # Spread mínimo de 2% para considerar
    
    def find_opportunities(self, markets: List[Market]) -> List[ProbabilityArbitrageOpportunity]:
        """
        Encontra oportunidades de arbitragem por probabilidade
        
        Args:
            markets: Lista de todos os mercados de todas as exchanges
            
        Returns:
            Lista de oportunidades de arbitragem
        """
        opportunities = []
        
        # Encontra pares de mercados equivalentes entre exchanges diferentes
        matches = self.matcher.find_matching_events(markets)
        
        print(f"[Probability Arbitrage] Analisando {len(matches)} matches entre exchanges...")
        
        for market1, market2 in matches:
            # Só compara mercados de exchanges diferentes
            if market1.exchange == market2.exchange:
                continue
            
            # Calcula confiança do matching
            confidence = self.matcher.calculate_enhanced_similarity(
                market1.question,
                market2.question
            )
            
            # Verifica se são outcomes compatíveis
            # Pode ser mesmo outcome (YES vs YES) ou opostos (YES vs NO)
            opp = self._calculate_probability_arbitrage(market1, market2, confidence)
            
            if opp:
                opportunities.append(opp)
        
        print(f"[Probability Arbitrage] {len(opportunities)} oportunidades encontradas")
        return opportunities
    
    def _calculate_probability_arbitrage(
        self,
        market1: Market,
        market2: Market,
        confidence: float
    ) -> Optional[ProbabilityArbitrageOpportunity]:
        """
        Calcula oportunidade de arbitragem entre dois mercados equivalentes
        
        Considera dois cenários:
        1. Mesmo outcome (YES vs YES): Compara probabilidades diretamente
        2. Outcomes opostos (YES vs NO): Compara YES com (1 - NO)
        """
        
        # Verifica liquidez mínima
        if market1.liquidity < self.min_liquidity or market2.liquidity < self.min_liquidity:
            return None
        
        # Normaliza probabilidades para o mesmo outcome
        prob1 = market1.price
        prob2 = market2.price
        
        # Se outcomes são opostos, ajusta
        if market1.outcome != market2.outcome:
            # Se um é YES e outro NO, compara YES com (1 - NO)
            if market1.outcome.upper() == "YES":
                prob2 = 1.0 - prob2  # Converte NO para YES
            else:
                prob1 = 1.0 - prob1  # Converte NO para YES
        
        # Calcula spread
        spread = abs(prob1 - prob2)
        spread_pct = spread
        
        # Se spread é muito pequeno, não há oportunidade
        if spread_pct < self.min_spread:
            return None
        
        # Identifica qual tem probabilidade menor (comprar) e maior (vender)
        if prob1 < prob2:
            market_low = market1
            market_high = market2
            prob_low = prob1
            prob_high = prob2
        else:
            market_low = market2
            market_high = market1
            prob_low = prob2
            prob_high = prob1
        
        # Calcula lucro bruto
        # Estratégia: Comprar no mercado com menor probabilidade, vender no maior
        investment = 100.0  # Assume $100 de investimento
        
        # Compra no mercado com menor probabilidade
        shares_buy = investment / prob_low
        
        # Vende no mercado com maior probabilidade
        revenue = shares_buy * prob_high
        
        # Calcula taxas
        fee_buy = EXCHANGE_FEES.get(market_low.exchange.lower(), 0.05)
        fee_sell = EXCHANGE_FEES.get(market_high.exchange.lower(), 0.05)
        
        # Taxas de gas (se aplicável)
        gas_buy = GAS_FEES.get(market_low.exchange.lower(), 0)
        gas_sell = GAS_FEES.get(market_high.exchange.lower(), 0)
        
        fees = (investment * fee_buy) + (revenue * fee_sell) + (gas_buy + gas_sell) * 3000
        net_profit = revenue - investment - fees
        profit_pct = net_profit / investment
        
        # Verifica se o lucro é suficiente
        if profit_pct < self.min_profit:
            return None
        
        # Calcula scores usando funções melhoradas
        markets_list = [market_low, market_high]
        liquidity_score = calculate_liquidity_score(markets_list)
        risk_score = calculate_risk_score(
            markets_list,
            profit_pct,
            confidence,
            strategy="probability_spread"
        )
        
        # Calcula quality_score
        quality_score = calculate_quality_score(
            profit_pct,
            confidence,
            liquidity_score,
            risk_score,
            spread_pct=spread_pct
        )
        
        # Determina nível de risco
        risk_level = get_risk_level(risk_score)
        
        # Cria explicação
        outcome_str = market_low.outcome if market_low.outcome == market_high.outcome else "YES"
        explanation = (
            f"Spread de {spread_pct:.1%} entre exchanges. "
            f"Comprar em {market_low.exchange} ({prob_low:.1%}) e "
            f"vender em {market_high.exchange} ({prob_high:.1%})."
        )
        
        return ProbabilityArbitrageOpportunity(
            market_low=market_low,
            market_high=market_high,
            probability_low=prob_low,
            probability_high=prob_high,
            spread_pct=spread_pct,
            profit_pct=profit_pct,
            profit_abs=net_profit,
            fees=fees,
            net_profit=net_profit,
            confidence=confidence,
            explanation=explanation,
            risk_score=risk_score,
            liquidity_score=liquidity_score,
            quality_score=quality_score,
            risk_level=risk_level
        )

