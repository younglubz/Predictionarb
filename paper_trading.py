"""Sistema de paper trading para simular arbitragem sem risco"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from arbitrage import ArbitrageOpportunity
from exchanges.base import Market


@dataclass
class PaperTrade:
    """Representa um trade simulado"""
    opportunity: ArbitrageOpportunity
    entry_time: datetime
    exit_time: Optional[datetime]
    entry_price_buy: float
    entry_price_sell: float
    exit_price_buy: Optional[float] = None
    exit_price_sell: Optional[float] = None
    amount: float = 100.0  # Valor investido
    realized_profit: Optional[float] = None
    status: str = "pending"  # pending, executed, closed, failed
    
    def calculate_potential_profit(self) -> float:
        """Calcula lucro potencial"""
        return self.opportunity.net_profit * (self.amount / 100.0)
    
    def execute(self) -> bool:
        """Simula execução do trade"""
        if self.status != "pending":
            return False
        
        # Simula execução (assume que preços ainda estão válidos)
        self.status = "executed"
        self.exit_time = datetime.now()
        self.realized_profit = self.calculate_potential_profit()
        return True


class PaperTradingEngine:
    """Engine de paper trading para testar estratégias"""
    
    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.trades: List[PaperTrade] = []
        self.open_positions: List[PaperTrade] = []
    
    def evaluate_opportunity(self, opportunity: ArbitrageOpportunity) -> Dict:
        """Avalia uma oportunidade de arbitragem"""
        # Verifica se há liquidez suficiente
        min_liquidity = min(opportunity.market_buy.liquidity, opportunity.market_sell.liquidity)
        
        # Verifica se o lucro compensa
        min_profit_pct = 0.02  # 2% mínimo
        
        evaluation = {
            "viable": opportunity.profit_pct >= min_profit_pct and min_liquidity >= 100,
            "profit_pct": opportunity.profit_pct,
            "profit_abs": opportunity.net_profit,
            "liquidity": min_liquidity,
            "confidence": opportunity.confidence,
            "recommended_amount": min(min_liquidity * 0.1, self.balance * 0.1)  # 10% da liquidez ou 10% do balance
        }
        
        return evaluation
    
    def simulate_trade(self, opportunity: ArbitrageOpportunity, amount: Optional[float] = None) -> PaperTrade:
        """Simula um trade de arbitragem"""
        if amount is None:
            amount = min(opportunity.market_buy.liquidity * 0.1, self.balance * 0.1, 1000.0)
        
        if amount > self.balance:
            raise ValueError("Saldo insuficiente")
        
        trade = PaperTrade(
            opportunity=opportunity,
            entry_time=datetime.now(),
            exit_time=None,
            entry_price_buy=opportunity.buy_price,
            entry_price_sell=opportunity.sell_price,
            amount=amount,
            status="pending"
        )
        
        # Executa o trade
        if trade.execute():
            self.balance -= amount
            self.balance += amount + trade.realized_profit
            self.trades.append(trade)
            self.open_positions.append(trade)
        
        return trade
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas do paper trading"""
        if not self.trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "total_profit": 0.0,
                "roi": 0.0,
                "current_balance": self.balance
            }
        
        winning = [t for t in self.trades if t.realized_profit and t.realized_profit > 0]
        losing = [t for t in self.trades if t.realized_profit and t.realized_profit <= 0]
        
        total_profit = sum(t.realized_profit for t in self.trades if t.realized_profit)
        roi = (total_profit / self.initial_balance) * 100 if self.initial_balance > 0 else 0
        
        return {
            "total_trades": len(self.trades),
            "winning_trades": len(winning),
            "losing_trades": len(losing),
            "win_rate": len(winning) / len(self.trades) if self.trades else 0,
            "total_profit": total_profit,
            "roi": roi,
            "current_balance": self.balance,
            "initial_balance": self.initial_balance
        }

