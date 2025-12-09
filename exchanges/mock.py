"""Exchange mock para testes"""
from typing import List
from exchanges.base import ExchangeBase, Market
from datetime import datetime, timedelta

class MockExchange(ExchangeBase):
    def __init__(self):
        super().__init__("mock")
    
    def normalize_question(self, question: str) -> str:
        return question.lower().strip()
    
    async def fetch_markets(self) -> List[Market]:
        markets = []
        base_time = datetime.now() + timedelta(days=30)
        mock_data = [
            {"question": "Bitcoin price will be above $50,000 by end of 2024", "price_yes": 0.65, "price_no": 0.35, "volume": 10000, "liquidity": 5000},
            {"question": "Ethereum will reach $3000 by December 2024", "price_yes": 0.70, "price_no": 0.30, "volume": 8000, "liquidity": 4000},
        ]
        for i, data in enumerate(mock_data):
            market_id = f"mock_{i}"
            markets.append(Market(exchange=self.name, market_id=f"{market_id}_yes", question=data["question"], outcome="YES", price=data["price_yes"], volume_24h=data["volume"], liquidity=data["liquidity"], expires_at=base_time, url=f"https://mock.example.com/{market_id}"))
            markets.append(Market(exchange=self.name, market_id=f"{market_id}_no", question=data["question"], outcome="NO", price=data["price_no"], volume_24h=data["volume"], liquidity=data["liquidity"], expires_at=base_time, url=f"https://mock.example.com/{market_id}"))
        return markets
