"""
Arbitragem Combinatória - Baseado em pesquisa sobre Polymarket

Dois tipos principais:
1. Arbitragem de Reequilíbrio: Dentro de um único mercado/condição
2. Arbitragem Combinatória: Entre múltiplos mercados interligados

Referência: Estudo empírico mostra ~$40 milhões extraídos via arbitragem
"""
from typing import List, Tuple, Optional
from exchanges.base import Market
from dataclasses import dataclass, field
from config import EXCHANGE_FEES
from scoring_utils import calculate_liquidity_score, calculate_risk_score, calculate_quality_score, get_risk_level
import re


@dataclass
class CombinatorialOpportunity:
    """Oportunidade de arbitragem combinatória"""
    markets: List[Market]
    strategy: str  # "complementary" ou "related"
    total_probability: float  # Soma das probabilidades
    expected_profit_pct: float
    confidence: float
    explanation: str
    risk_score: float = field(default=0.0)  # Score numérico de risco (0-1)
    liquidity_score: float = field(default=0.0)  # Score de liquidez (0-1)
    quality_score: float = field(default=0.0)  # Score de qualidade (0-100)
    risk_level: str = field(default="médio")  # Nível de risco textual
    

class CombinatorialArbitrage:
    """
    Detecta arbitragem combinatória entre mercados relacionados
    
    Exemplo: Se P(A) + P(B) > 1.0 onde A e B são mutuamente exclusivos,
    há arbitragem vendendo ambos.
    """
    
    def __init__(self):
        self.min_profit = 0.01  # 1% lucro mínimo
        
    def find_complementary_markets(self, markets: List[Market]) -> List[Tuple[Market, Market]]:
        """
        Encontra mercados complementares (YES/NO do mesmo evento)
        
        Exemplo: "Will X happen? - Yes" e "Will X happen? - No"
        Idealmente P(Yes) + P(No) = 1.0
        """
        complementary_pairs = []
        
        for i, m1 in enumerate(markets):
            for m2 in markets[i+1:]:
                # Mesmo exchange e mercado base
                if m1.exchange != m2.exchange:
                    continue
                
                # Verifica se são YES/NO do mesmo evento
                q1_clean = m1.question.lower().replace(m1.outcome.lower(), "").strip()
                q2_clean = m2.question.lower().replace(m2.outcome.lower(), "").strip()
                
                # Se as perguntas são iguais (sem o outcome)
                if q1_clean == q2_clean:
                    # E os outcomes são opostos
                    if self._are_complementary_outcomes(m1.outcome, m2.outcome):
                        complementary_pairs.append((m1, m2))
        
        return complementary_pairs
    
    def _are_complementary_outcomes(self, outcome1: str, outcome2: str) -> bool:
        """Verifica se dois outcomes são complementares (Yes/No)"""
        o1 = outcome1.lower().strip()
        o2 = outcome2.lower().strip()
        
        complementary_sets = [
            {"yes", "no"},
            {"true", "false"},
            {"will", "won't"},
            {"republican", "democratic"},  # Dois partidos principais
        ]
        
        for comp_set in complementary_sets:
            if o1 in comp_set and o2 in comp_set and o1 != o2:
                return True
        
        return False
    
    def check_complementary_arbitrage(
        self, 
        market1: Market, 
        market2: Market
    ) -> Optional[CombinatorialOpportunity]:
        """
        Verifica arbitragem em mercados complementares
        
        Teoria: P(Yes) + P(No) deve ser = 1.0
        Se P(Yes) + P(No) < 1.0: comprar ambos (lucro garantido)
        Se P(Yes) + P(No) > 1.0: vender ambos (requer margem)
        """
        total_prob = market1.price + market2.price
        
        # Arbitragem de COMPRA (probabilidades somam < 1.0)
        if total_prob < 0.98:  # Margem de 2% para custos
            investment = total_prob  # Custo total
            guaranteed_return = 1.0  # Um dos dois sempre paga $1
            profit = guaranteed_return - investment
            profit_pct = profit / investment
            
            # Desconta taxas
            fees = EXCHANGE_FEES.get(market1.exchange, 0.02) * 2  # Duas transações
            net_profit_pct = profit_pct - fees
            
            if net_profit_pct > self.min_profit:
                # Calcula scores
                markets_list = [market1, market2]
                liquidity_score = calculate_liquidity_score(markets_list)
                risk_score = calculate_risk_score(
                    markets_list,
                    net_profit_pct,
                    confidence=0.95,
                    strategy="complementary_buy"
                )
                quality_score = calculate_quality_score(
                    net_profit_pct,
                    confidence=0.95,
                    liquidity_score=liquidity_score,
                    risk_score=risk_score,
                    spread_pct=1.0 - total_prob  # Spread é o quanto falta para 1.0
                )
                risk_level = get_risk_level(risk_score)
                
                return CombinatorialOpportunity(
                    markets=[market1, market2],
                    strategy="complementary_buy",
                    total_probability=total_prob,
                    expected_profit_pct=net_profit_pct,
                    confidence=0.95,  # Alta confiança - arbitragem matemática
                    explanation=f"Comprar ambos: ${total_prob:.4f} investido garante $1.00 retorno",
                    risk_score=risk_score,
                    liquidity_score=liquidity_score,
                    quality_score=quality_score,
                    risk_level=risk_level
                )
        
        # Arbitragem de VENDA (probabilidades somam > 1.0)
        elif total_prob > 1.02:  # Margem de 2%
            # Vender ambos - mais arriscado, requer margem
            premium = total_prob - 1.0
            profit_pct = premium / total_prob
            
            fees = EXCHANGE_FEES.get(market1.exchange, 0.02) * 2
            net_profit_pct = profit_pct - fees
            
            if net_profit_pct > self.min_profit:
                # Calcula scores
                markets_list = [market1, market2]
                liquidity_score = calculate_liquidity_score(markets_list)
                risk_score = calculate_risk_score(
                    markets_list,
                    net_profit_pct,
                    confidence=0.85,
                    strategy="complementary_sell"  # Venda aumenta risco
                )
                quality_score = calculate_quality_score(
                    net_profit_pct,
                    confidence=0.85,
                    liquidity_score=liquidity_score,
                    risk_score=risk_score,
                    spread_pct=total_prob - 1.0  # Spread é o quanto passa de 1.0
                )
                risk_level = get_risk_level(risk_score)
                
                return CombinatorialOpportunity(
                    markets=[market1, market2],
                    strategy="complementary_sell",
                    total_probability=total_prob,
                    expected_profit_pct=net_profit_pct,
                    confidence=0.85,  # Menor confiança - requer margem
                    explanation=f"Vender ambos: Probabilidades somam {total_prob:.4f} > 1.0",
                    risk_score=risk_score,
                    liquidity_score=liquidity_score,
                    quality_score=quality_score,
                    risk_level=risk_level
                )
        
        return None
    
    def find_related_arbitrage(
        self,
        markets: List[Market]
    ) -> List[CombinatorialOpportunity]:
        """
        Encontra arbitragem entre mercados relacionados logicamente
        
        Exemplo: "A vence eleição" vs "Partido de A vence eleição"
        Se P(A vence) > P(Partido de A vence), há incoerência lógica
        """
        opportunities = []
        
        # Agrupa mercados por tema/ano
        themed_groups = self._group_by_theme(markets)
        
        for theme, group_markets in themed_groups.items():
            if len(group_markets) < 2:
                continue
            
            # Procura relações lógicas
            for i, m1 in enumerate(group_markets):
                for m2 in group_markets[i+1:]:
                    opp = self._check_logical_consistency(m1, m2)
                    if opp:
                        opportunities.append(opp)
        
        return opportunities
    
    def _group_by_theme(self, markets: List[Market]) -> dict:
        """Agrupa mercados por tema (extrai palavras-chave)"""
        groups = {}
        
        for market in markets:
            # Extrai ano
            years = re.findall(r'\b(202[4-9]|203[0-9])\b', market.question)
            year = years[0] if years else "no_year"
            
            # Extrai tema principal (primeiras 3 palavras significativas)
            words = market.question.lower().split()
            significant_words = [w for w in words if len(w) > 3][:3]
            theme = f"{year}_{' '.join(significant_words)}"
            
            if theme not in groups:
                groups[theme] = []
            groups[theme].append(market)
        
        return groups
    
    def _check_logical_consistency(
        self,
        market1: Market,
        market2: Market
    ) -> Optional[CombinatorialOpportunity]:
        """
        Verifica consistência lógica entre dois mercados
        
        Exemplo: Se "Biden vence" tem P=0.6 mas "Democrata vence" tem P=0.4,
        há incoerência (Biden é democrata, então P(Biden) <= P(Democrata))
        """
        # Esta é uma versão simplificada
        # Versão completa requer ontologia de relações lógicas
        
        # Por ora, apenas detecta inconsistências óbvias de probabilidade
        # quando mercados têm overlap temático
        
        return None  # Implementação futura
    
    def find_all_opportunities(
        self,
        markets: List[Market]
    ) -> List[CombinatorialOpportunity]:
        """Encontra todas as oportunidades de arbitragem combinatória"""
        opportunities = []
        
        # 1. Arbitragem complementar (Yes/No)
        complementary_pairs = self.find_complementary_markets(markets)
        print(f"\n[Combinatorial] Encontrados {len(complementary_pairs)} pares complementares")
        
        for m1, m2 in complementary_pairs:
            opp = self.check_complementary_arbitrage(m1, m2)
            if opp:
                opportunities.append(opp)
                print(f"  ✓ Oportunidade: {opp.strategy} - {opp.expected_profit_pct*100:.2f}%")
        
        # 2. Arbitragem relacionada (lógica)
        related_opps = self.find_related_arbitrage(markets)
        opportunities.extend(related_opps)
        
        print(f"[Combinatorial] Total: {len(opportunities)} oportunidades\n")
        
        return opportunities

