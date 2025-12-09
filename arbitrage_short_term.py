"""
Arbitragem de Curto Prazo - Trades Rápidos (Diários)

Este módulo identifica oportunidades de arbitragem baseadas em:
1. Flutuações rápidas de porcentagem entre exchanges
2. Discrepâncias temporárias de preço
3. Mercados que expiram em breve (para fechar posição rapidamente)
4. Volatilidade e spreads que aparecem e desaparecem rapidamente

Estratégia:
- Foca em trades que podem ser fechados no mesmo dia
- Detecta mudanças súbitas nos preços
- Identifica oportunidades que podem desaparecer rapidamente
- Prioriza mercados com alta liquidez para execução rápida
"""
from typing import List, Optional, Tuple, Dict
from exchanges.base import Market
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from config import MIN_ARBITRAGE_PROFIT, MIN_LIQUIDITY, EXCHANGE_FEES, GAS_FEES
from matcher_improved import ImprovedEventMatcher
from scoring_utils import calculate_liquidity_score, calculate_risk_score, calculate_quality_score, get_risk_level


@dataclass
class ShortTermArbitrageOpportunity:
    """Oportunidade de arbitragem de curto prazo"""
    market_low: Market      # Exchange com menor probabilidade (comprar)
    market_high: Market     # Exchange com maior probabilidade (vender)
    probability_low: float  # Probabilidade menor
    probability_high: float # Probabilidade maior
    spread_pct: float       # Diferença percentual
    profit_pct: float       # Lucro percentual após taxas
    profit_abs: float       # Lucro absoluto
    fees: float
    net_profit: float
    confidence: float       # Confiança no matching
    time_to_expiry_hours: float  # Horas até expiração
    volatility_score: float # Score de volatilidade (0-1)
    execution_speed: str    # "rápido", "médio", "lento"
    explanation: str
    risk_level: str         # "baixo", "médio", "alto"
    risk_score: float = field(default=0.0)  # Score numérico de risco (0-1)
    liquidity_score: float = field(default=0.0)  # Score de liquidez (0-1)
    quality_score: float = field(default=0.0)  # Score de qualidade (0-100)
    
    def __str__(self):
        return (
            f"Arbitragem Curto Prazo: {self.profit_pct:.2%} lucro\n"
            f"  Spread: {self.spread_pct:.2%} ({self.probability_low:.1%} vs {self.probability_high:.1%})\n"
            f"  Comprar: {self.market_low.exchange} @ {self.probability_low:.1%}\n"
            f"  Vender: {self.market_high.exchange} @ {self.probability_high:.1%}\n"
            f"  Tempo até expiração: {self.time_to_expiry_hours:.1f}h\n"
            f"  Velocidade de execução: {self.execution_speed}\n"
            f"  Risco: {self.risk_level}\n"
            f"  Lucro líquido: ${self.net_profit:.2f} (${100} investido)\n"
            f"  Confiança: {self.confidence:.1%}"
        )


class ShortTermArbitrageEngine:
    """
    Detecta oportunidades de arbitragem de curto prazo
    
    Foco em:
    - Trades que podem ser fechados rapidamente (mesmo dia)
    - Flutuações temporárias de preço
    - Mercados com expiração próxima
    - Alta liquidez para execução rápida
    """
    
    def __init__(self, matcher: ImprovedEventMatcher):
        self.matcher = matcher
        self.min_profit = MIN_ARBITRAGE_PROFIT
        self.min_liquidity = MIN_LIQUIDITY * 2  # Maior liquidez para trades rápidos
        self.min_spread = 0.03  # Spread mínimo de 3% para considerar
        self.max_expiry_hours = 48  # Máximo 48h até expiração (foco em curto prazo)
        self.min_expiry_hours = 1  # Mínimo 1h (evita mercados que expiram muito em breve)
    
    def find_opportunities(self, markets: List[Market]) -> List[ShortTermArbitrageOpportunity]:
        """
        Encontra oportunidades de arbitragem de curto prazo
        
        Args:
            markets: Lista de todos os mercados de todas as exchanges
            
        Returns:
            Lista de oportunidades de curto prazo
        """
        opportunities = []
        
        # Filtra mercados com expiração próxima (curto prazo)
        short_term_markets = self._filter_short_term_markets(markets)
        
        print(f"[Short-Term Arbitrage] Analisando {len(short_term_markets)} mercados de curto prazo...")
        
        # Encontra pares de mercados equivalentes entre exchanges diferentes
        matches = self.matcher.find_matching_events(short_term_markets)
        
        print(f"[Short-Term Arbitrage] {len(matches)} matches encontrados...")
        
        for market1, market2 in matches:
            # Só compara mercados de exchanges diferentes
            if market1.exchange == market2.exchange:
                continue
            
            # Calcula confiança do matching
            confidence = self.matcher.calculate_enhanced_similarity(
                market1.question,
                market2.question
            )
            
            # Verifica se são outcomes compatíveis e se há oportunidade
            opp = self._calculate_short_term_arbitrage(market1, market2, confidence)
            
            if opp:
                opportunities.append(opp)
        
        # Ordena por lucro e velocidade de execução
        opportunities.sort(key=lambda x: (x.profit_pct, -x.time_to_expiry_hours), reverse=True)
        
        print(f"[Short-Term Arbitrage] {len(opportunities)} oportunidades de curto prazo encontradas")
        return opportunities
    
    def _filter_short_term_markets(self, markets: List[Market]) -> List[Market]:
        """Filtra mercados com expiração em curto prazo (1-48h)"""
        now = datetime.now()
        
        filtered = []
        for market in markets:
            if not market.expires_at:
                continue
            
            # Garante timezone-aware
            expiry = market.expires_at
            if expiry.tzinfo is None and now.tzinfo:
                expiry = expiry.replace(tzinfo=now.tzinfo)
            elif expiry.tzinfo and now.tzinfo is None:
                now = now.replace(tzinfo=expiry.tzinfo)
            
            hours_to_expiry = (expiry - now).total_seconds() / 3600
            
            # Filtra por janela de tempo
            if self.min_expiry_hours <= hours_to_expiry <= self.max_expiry_hours:
                # Prioriza alta liquidez
                if market.liquidity >= self.min_liquidity:
                    filtered.append(market)
        
        return filtered
    
    def _calculate_short_term_arbitrage(
        self,
        market1: Market,
        market2: Market,
        confidence: float
    ) -> Optional[ShortTermArbitrageOpportunity]:
        """
        Calcula oportunidade de arbitragem de curto prazo
        
        Considera:
        - Spread de probabilidade
        - Tempo até expiração
        - Liquidez (para execução rápida)
        - Volatilidade estimada
        """
        
        # Verifica liquidez mínima (maior para trades rápidos)
        if market1.liquidity < self.min_liquidity or market2.liquidity < self.min_liquidity:
            return None
        
        # Verifica tempo até expiração
        now = datetime.now()
        
        expiry1 = market1.expires_at
        expiry2 = market2.expires_at
        
        if not expiry1 or not expiry2:
            return None
        
        # Garante timezone-aware
        if now.tzinfo is None and expiry1.tzinfo:
            now = now.replace(tzinfo=expiry1.tzinfo)
        elif now.tzinfo and expiry1.tzinfo is None:
            expiry1 = expiry1.replace(tzinfo=now.tzinfo)
        
        if expiry2.tzinfo is None and now.tzinfo:
            expiry2 = expiry2.replace(tzinfo=now.tzinfo)
        
        hours_to_expiry1 = (expiry1 - now).total_seconds() / 3600
        hours_to_expiry2 = (expiry2 - now).total_seconds() / 3600
        
        # Usa o menor tempo até expiração (mais urgente)
        time_to_expiry_hours = min(hours_to_expiry1, hours_to_expiry2)
        
        # Verifica se está na janela de tempo
        if not (self.min_expiry_hours <= time_to_expiry_hours <= self.max_expiry_hours):
            return None
        
        # Normaliza probabilidades para o mesmo outcome
        prob1 = market1.price
        prob2 = market2.price
        
        # Se outcomes são opostos, ajusta
        if market1.outcome != market2.outcome:
            if market1.outcome.upper() == "YES":
                prob2 = 1.0 - prob2
            else:
                prob1 = 1.0 - prob1
        
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
            strategy="short_term",
            time_to_expiry_hours=time_to_expiry_hours
        )
        
        # Calcula score de volatilidade (baseado em spread e liquidez)
        avg_liquidity = (market_low.liquidity + market_high.liquidity) / 2
        volatility_score = min(spread_pct * 2, 1.0)  # Spread maior = mais volatilidade
        
        # Calcula quality_score
        quality_score = calculate_quality_score(
            profit_pct,
            confidence,
            liquidity_score,
            risk_score,
            spread_pct=spread_pct,
            volatility_score=volatility_score
        )
        
        # Determina velocidade de execução
        if avg_liquidity > 10000 and spread_pct > 0.05:
            execution_speed = "rápido"
        elif avg_liquidity > 5000:
            execution_speed = "médio"
        else:
            execution_speed = "lento"
        
        # Determina nível de risco baseado no risk_score numérico
        risk_level = get_risk_level(risk_score)
        
        # Cria explicação
        outcome_str = market_low.outcome if market_low.outcome == market_high.outcome else "YES"
        explanation = (
            f"Oportunidade de curto prazo detectada! "
            f"Spread de {spread_pct:.1%} entre {market_low.exchange} ({prob_low:.1%}) e "
            f"{market_high.exchange} ({prob_high:.1%}). "
            f"Expira em {time_to_expiry_hours:.1f}h. "
            f"Execução: {execution_speed}, Risco: {risk_level}."
        )
        
        return ShortTermArbitrageOpportunity(
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
            time_to_expiry_hours=time_to_expiry_hours,
            volatility_score=volatility_score,
            execution_speed=execution_speed,
            explanation=explanation,
            risk_level=risk_level,
            risk_score=risk_score,
            liquidity_score=liquidity_score,
            quality_score=quality_score
        )

