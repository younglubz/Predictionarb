"""Classe base para integrações com exchanges"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Market:
    """Representa um mercado de previsão"""
    exchange: str
    market_id: str
    question: str
    outcome: str  # "YES" ou "NO"
    price: float  # 0.0 a 1.0
    volume_24h: float
    liquidity: float
    expires_at: Optional[datetime]
    url: Optional[str] = None
    
    def __hash__(self):
        return hash((self.exchange, self.market_id, self.outcome))
    
    def __eq__(self, other):
        if not isinstance(other, Market):
            return False
        return (self.exchange == other.exchange and 
                self.market_id == other.market_id and 
                self.outcome == other.outcome)


class ExchangeBase(ABC):
    """Interface base para exchanges de prediction markets"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def fetch_markets(self) -> List[Market]:
        """Busca todos os mercados ativos"""
        pass
    
    @abstractmethod
    def normalize_question(self, question: str) -> str:
        """Normaliza a pergunta para facilitar matching"""
        pass
    
    def calculate_fee(self, amount: float) -> float:
        """Calcula taxa de transação"""
        from config import EXCHANGE_FEES
        fee_pct = EXCHANGE_FEES.get(self.name.lower(), 0.05)
        return amount * fee_pct

