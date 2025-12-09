"""
Modo Simulação - Permite ao usuário testar tudo sem executar trades reais

Funcionalidades:
- Simula execução de arbitragem
- Calcula lucros/perdas potenciais
- Testa estratégias sem risco
- Analisa oportunidades antes de operar capital próprio
- Tracking de performance simulada
"""
from typing import List, Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime
from exchanges.base import Market
from arbitrage import ArbitrageOpportunity
import json


@dataclass
class SimulatedTrade:
    """Representa um trade simulado"""
    id: str
    opportunity: ArbitrageOpportunity
    entry_time: datetime
    amount_usd: float
    
    # Preços de entrada
    buy_price: float
    sell_price: float
    
    # Custos
    buy_fee: float
    sell_fee: float
    gas_fee: float = 0.0
    
    # Resultados
    gross_profit: float = 0.0
    net_profit: float = 0.0
    profit_pct: float = 0.0
    
    # Status
    status: str = "pending"  # pending, executed, closed
    exit_time: Optional[datetime] = None
    
    # Observações
    notes: List[str] = field(default_factory=list)
    
    def execute(self):
        """Simula execução do trade"""
        if self.status != "pending":
            return
        
        # Calcula lucro bruto
        self.gross_profit = (self.sell_price - self.buy_price) * self.amount_usd
        
        # Calcula custos totais
        total_costs = (self.buy_fee + self.sell_fee + self.gas_fee) * self.amount_usd
        
        # Lucro líquido
        self.net_profit = self.gross_profit - total_costs
        
        # Percentual
        self.profit_pct = self.net_profit / self.amount_usd if self.amount_usd > 0 else 0
        
        self.status = "executed"
        self.exit_time = datetime.now()


class SimulationEngine:
    """
    Engine de simulação para testar arbitragem sem risco
    
    Permite:
    - Testar oportunidades identificadas
    - Simular diferentes tamanhos de trade
    - Analisar impacto de taxas e slippage
    - Comparar estratégias
    - Ver histórico de performance
    """
    
    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.trades: List[SimulatedTrade] = []
        self.trade_counter = 0
    
    def simulate_trade(
        self,
        opportunity: ArbitrageOpportunity,
        amount_usd: Optional[float] = None,
        include_slippage: bool = True,
        slippage_pct: float = 0.01
    ) -> SimulatedTrade:
        """
        Simula execução de uma oportunidade de arbitragem
        
        Args:
            opportunity: Oportunidade a simular
            amount_usd: Valor a investir (None = calcular automaticamente)
            include_slippage: Incluir slippage na simulação
            slippage_pct: Percentual de slippage (1% = 0.01)
        
        Returns:
            SimulatedTrade: Trade simulado com resultados
        """
        # Calcula valor a investir
        if amount_usd is None:
            # Usa 10% da liquidez disponível ou 10% do balance
            max_by_liquidity = min(
                opportunity.market_buy.liquidity * 0.1,
                opportunity.market_sell.liquidity * 0.1
            )
            max_by_balance = self.balance * 0.1
            amount_usd = min(max_by_liquidity, max_by_balance, 1000.0)
        
        # Verifica se tem saldo suficiente
        if amount_usd > self.balance:
            amount_usd = self.balance
        
        # Aplica slippage se configurado
        buy_price = opportunity.buy_price
        sell_price = opportunity.sell_price
        
        if include_slippage:
            # Slippage negativo (piora o preço)
            buy_price *= (1 + slippage_pct)  # Compra fica mais cara
            sell_price *= (1 - slippage_pct)  # Venda fica mais barata
        
        # Cria trade
        self.trade_counter += 1
        trade = SimulatedTrade(
            id=f"SIM_{self.trade_counter:04d}",
            opportunity=opportunity,
            entry_time=datetime.now(),
            amount_usd=amount_usd,
            buy_price=buy_price,
            sell_price=sell_price,
            buy_fee=opportunity.fees / 2,  # Divide fees entre buy e sell
            sell_fee=opportunity.fees / 2,
            gas_fee=0.001  # Estimativa conservadora
        )
        
        # Executa
        trade.execute()
        
        # Atualiza balance
        self.balance += trade.net_profit
        
        # Adiciona notas
        if include_slippage:
            trade.notes.append(f"Slippage de {slippage_pct:.2%} aplicado")
        
        trade.notes.append(f"Balance após: ${self.balance:.2f}")
        
        # Salva
        self.trades.append(trade)
        
        return trade
    
    def simulate_multiple(
        self,
        opportunities: List[ArbitrageOpportunity],
        amount_per_trade: Optional[float] = None
    ) -> Dict:
        """
        Simula múltiplas oportunidades
        
        Returns:
            Dict: Estatísticas agregadas
        """
        results = {
            "total_opportunities": len(opportunities),
            "simulated_trades": 0,
            "total_invested": 0.0,
            "total_profit": 0.0,
            "avg_profit_pct": 0.0,
            "best_trade": None,
            "worst_trade": None
        }
        
        if not opportunities:
            return results
        
        for opp in opportunities:
            trade = self.simulate_trade(opp, amount_per_trade)
            results["simulated_trades"] += 1
            results["total_invested"] += trade.amount_usd
            results["total_profit"] += trade.net_profit
        
        # Calcula médias
        if results["simulated_trades"] > 0:
            results["avg_profit_pct"] = results["total_profit"] / results["total_invested"]
        
        # Encontra melhor e pior
        if self.trades:
            results["best_trade"] = max(self.trades, key=lambda t: t.profit_pct)
            results["worst_trade"] = min(self.trades, key=lambda t: t.profit_pct)
        
        return results
    
    def get_statistics(self) -> Dict:
        """
        Retorna estatísticas completas da simulação
        
        Returns:
            Dict: Estatísticas detalhadas
        """
        if not self.trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "total_invested": 0.0,
                "total_profit": 0.0,
                "avg_profit": 0.0,
                "roi": 0.0,
                "current_balance": self.balance,
                "initial_balance": self.initial_balance
            }
        
        winning = [t for t in self.trades if t.net_profit > 0]
        losing = [t for t in self.trades if t.net_profit <= 0]
        
        total_invested = sum(t.amount_usd for t in self.trades)
        total_profit = sum(t.net_profit for t in self.trades)
        
        return {
            "total_trades": len(self.trades),
            "winning_trades": len(winning),
            "losing_trades": len(losing),
            "win_rate": len(winning) / len(self.trades) if self.trades else 0,
            "total_invested": total_invested,
            "total_profit": total_profit,
            "avg_profit": total_profit / len(self.trades) if self.trades else 0,
            "avg_profit_pct": total_profit / total_invested if total_invested > 0 else 0,
            "roi": (self.balance - self.initial_balance) / self.initial_balance,
            "current_balance": self.balance,
            "initial_balance": self.initial_balance,
            "best_trade": max(self.trades, key=lambda t: t.profit_pct),
            "worst_trade": min(self.trades, key=lambda t: t.profit_pct)
        }
    
    def export_report(self, filename: str = "simulation_report.json"):
        """Exporta relatório completo da simulação"""
        stats = self.get_statistics()
        
        report = {
            "simulation_info": {
                "initial_balance": self.initial_balance,
                "final_balance": self.balance,
                "total_trades": len(self.trades),
                "generated_at": datetime.now().isoformat()
            },
            "statistics": stats,
            "trades": [
                {
                    "id": t.id,
                    "entry_time": t.entry_time.isoformat(),
                    "exit_time": t.exit_time.isoformat() if t.exit_time else None,
                    "amount_usd": t.amount_usd,
                    "buy_exchange": t.opportunity.market_buy.exchange,
                    "sell_exchange": t.opportunity.market_sell.exchange,
                    "buy_price": t.buy_price,
                    "sell_price": t.sell_price,
                    "net_profit": t.net_profit,
                    "profit_pct": t.profit_pct,
                    "notes": t.notes
                }
                for t in self.trades
            ]
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def reset(self):
        """Reseta a simulação"""
        self.balance = self.initial_balance
        self.trades = []
        self.trade_counter = 0

