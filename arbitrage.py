"""Engine de detecção de arbitragem"""
from typing import List, Tuple, Optional
from exchanges.base import Market
from config import MIN_ARBITRAGE_PROFIT, MIN_LIQUIDITY, EXCHANGE_FEES, GAS_FEES
from dataclasses import dataclass
from market_validator import MarketValidator


@dataclass
class ArbitrageOpportunity:
    """Representa uma oportunidade de arbitragem"""
    market_buy: Market      # Onde comprar (preço mais baixo)
    market_sell: Market     # Onde vender (preço mais alto)
    buy_price: float
    sell_price: float
    profit_pct: float       # Lucro percentual
    profit_abs: float       # Lucro absoluto (assumindo $100)
    fees: float
    net_profit: float
    confidence: float       # Confiança no matching (0-1)
    
    def __str__(self):
        return (
            f"Arbitragem: {self.profit_pct:.2%} lucro\n"
            f"  Comprar: {self.market_buy.exchange} @ ${self.buy_price:.4f}\n"
            f"  Vender: {self.market_sell.exchange} @ ${self.sell_price:.4f}\n"
            f"  Lucro líquido: ${self.net_profit:.2f} (${100} investido)\n"
            f"  Confiança: {self.confidence:.1%}"
        )


class ArbitrageEngine:
    """Detecta oportunidades de arbitragem"""
    
    def __init__(self):
        self.min_profit = MIN_ARBITRAGE_PROFIT
        self.min_liquidity = MIN_LIQUIDITY
        self.validator = MarketValidator()
    
    def calculate_arbitrage(
        self, 
        market1: Market, 
        market2: Market,
        confidence: float = 1.0
    ) -> Optional[ArbitrageOpportunity]:
        """Calcula se há oportunidade de arbitragem entre dois mercados"""
        
        # Valida equivalência dos mercados primeiro
        equivalent, validation = self.validator.validate_equivalence(market1, market2)
        if not equivalent:
            return None
        # Agora com validações ativas para evitar falsos positivos
        
        # Usa confiança da validação se for menor que a confiança passada
        confidence = min(confidence, validation.get("confidence", confidence))
        
        # Verifica liquidez mínima
        if market1.liquidity < self.min_liquidity or market2.liquidity < self.min_liquidity:
            return None
        
        # Identifica qual é mais barato e qual é mais caro
        if market1.price < market2.price:
            market_buy = market1
            market_sell = market2
            buy_price = market1.price
            sell_price = market2.price
        else:
            market_buy = market2
            market_sell = market1
            buy_price = market2.price
            sell_price = market1.price
        
        # Calcula lucro bruto
        profit_abs = sell_price - buy_price
        
        # Calcula taxas
        fee_buy = EXCHANGE_FEES.get(market_buy.exchange.lower(), 0.05)
        fee_sell = EXCHANGE_FEES.get(market_sell.exchange.lower(), 0.05)
        
        # Taxas de gas (se aplicável)
        gas_buy = GAS_FEES.get(market_buy.exchange.lower(), 0)
        gas_sell = GAS_FEES.get(market_sell.exchange.lower(), 0)
        
        # Assume investimento de $100 para cálculo
        investment = 100.0
        shares_buy = investment / buy_price
        revenue = shares_buy * sell_price
        
        fees = (investment * fee_buy) + (revenue * fee_sell) + (gas_buy + gas_sell) * 3000  # ETH ~$3000
        net_profit = revenue - investment - fees
        profit_pct = net_profit / investment
        
        # Verifica se o lucro é suficiente
        if profit_pct < self.min_profit:
            return None
        
        return ArbitrageOpportunity(
            market_buy=market_buy,
            market_sell=market_sell,
            buy_price=buy_price,
            sell_price=sell_price,
            profit_pct=profit_pct,
            profit_abs=profit_abs,
            fees=fees,
            net_profit=net_profit,
            confidence=confidence
        )
    
    def find_opportunities(
        self, 
        market_pairs: List[Tuple[Market, Market, float]]
    ) -> List[ArbitrageOpportunity]:
        """Encontra todas as oportunidades de arbitragem"""
        opportunities = []
        
        for market1, market2, confidence in market_pairs:
            # Verifica se são outcomes opostos (YES vs NO)
            if market1.outcome == market2.outcome:
                # Mesmo outcome - arbitragem direta
                opp = self.calculate_arbitrage(market1, market2, confidence)
                if opp:
                    opportunities.append(opp)
            else:
                # Outcomes opostos - pode fazer arbitragem combinada
                # Comprar YES barato + comprar NO barato, vender ambos caros
                # (implementação mais complexa, deixando para versão futura)
                pass
        
        # Ordena por lucro
        opportunities.sort(key=lambda x: x.profit_pct, reverse=True)
        
        return opportunities

