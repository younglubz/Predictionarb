"""Suporte a order books para análise de liquidez real"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Order:
    """Representa uma ordem no book"""
    price: float
    size: float  # Quantidade disponível
    side: str  # "buy" ou "sell"
    timestamp: Optional[datetime] = None


@dataclass
class OrderBook:
    """Order book de um mercado"""
    market_id: str
    exchange: str
    bids: List[Order]  # Ordens de compra (ordem decrescente de preço)
    asks: List[Order]  # Ordens de venda (ordem crescente de preço)
    last_update: Optional[datetime] = None
    
    def get_best_bid(self) -> Optional[Order]:
        """Retorna melhor oferta de compra"""
        return self.bids[0] if self.bids else None
    
    def get_best_ask(self) -> Optional[Order]:
        """Retorna melhor oferta de venda"""
        return self.asks[0] if self.asks else None
    
    def get_mid_price(self) -> Optional[float]:
        """Calcula preço médio entre bid e ask"""
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        
        if best_bid and best_ask:
            return (best_bid.price + best_ask.price) / 2.0
        elif best_bid:
            return best_bid.price
        elif best_ask:
            return best_ask.price
        return None
    
    def get_spread(self) -> Optional[float]:
        """Calcula spread (diferença entre ask e bid)"""
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        
        if best_bid and best_ask:
            return best_ask.price - best_bid.price
        return None
    
    def get_liquidity_at_price(self, price: float, side: str) -> float:
        """Calcula liquidez disponível em um preço específico"""
        orders = self.bids if side == "buy" else self.asks
        total = 0.0
        
        for order in orders:
            if side == "buy" and order.price >= price:
                total += order.size
            elif side == "sell" and order.price <= price:
                total += order.size
        
        return total

