"""Integração com Kalshi"""
import httpx
from typing import List
from exchanges.base import ExchangeBase, Market
from datetime import datetime
import re


class KalshiExchange(ExchangeBase):
    """Cliente para Kalshi API"""
    
    def __init__(self):
        super().__init__("kalshi")
        # Kalshi API mudou - usando nova URL (pode precisar de autenticação)
        self.base_url = "https://api.elections.kalshi.com/trade-api/v2"
    
    def normalize_question(self, question: str) -> str:
        """Normaliza pergunta"""
        normalized = re.sub(r'[^\w\s]', '', question.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    async def fetch_markets(self) -> List[Market]:
        """Busca mercados ativos do Kalshi"""
        markets = []
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Kalshi API - busca eventos ativos
                url = f"{self.base_url}/events"
                params = {
                    "limit": 100,
                    "status": "open"
                }
                
                response = await client.get(
                    url,
                    params=params,
                    headers={"Accept": "application/json"}
                )
                if response.status_code == 200:
                    data = response.json()
                    events = data.get("events", []) if isinstance(data, dict) else data
                    
                    for event_data in events:
                        try:
                            event_id = str(event_data.get("event_ticker", ""))
                            title = event_data.get("title", "")
                            
                            # Busca mercados do evento
                            markets_url = f"{self.base_url}/events/{event_id}/markets"
                            markets_response = await client.get(markets_url, timeout=10.0)
                            if markets_response.status_code == 200:
                                markets_data = markets_response.json()
                                market_list = markets_data.get("markets", [])
                                
                                for market_data in market_list:
                                    market_ticker = str(market_data.get("ticker", ""))
                                    question = market_data.get("title", title)
                                    
                                    # Kalshi tem Yes e No
                                    yes_price = float(market_data.get("yes_bid", 0) or 0) / 100.0
                                    no_price = float(market_data.get("no_bid", 0) or 0) / 100.0
                                    
                                    volume = float(market_data.get("volume", 0) or 0)
                                    liquidity = float(market_data.get("liquidity", volume * 0.1) or 0)
                                    
                                    end_date = market_data.get("expiration_time")
                                    market_url = f"https://kalshi.com/markets/{market_ticker}"
                                    
                                    expires_at = None
                                    if end_date:
                                        try:
                                            expires_at = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                                        except:
                                            pass
                                    
                                    # Cria mercado YES
                                    if yes_price > 0:
                                        market = Market(
                                            exchange=self.name,
                                            market_id=f"{event_id}_{market_ticker}_YES",
                                            question=question,
                                            outcome="YES",
                                            price=yes_price,
                                            volume_24h=volume,
                                            liquidity=liquidity,
                                            expires_at=expires_at,
                                            url=market_url
                                        )
                                        markets.append(market)
                                    
                                    # Cria mercado NO
                                    if no_price > 0:
                                        market = Market(
                                            exchange=self.name,
                                            market_id=f"{event_id}_{market_ticker}_NO",
                                            question=question,
                                            outcome="NO",
                                            price=no_price,
                                            volume_24h=volume,
                                            liquidity=liquidity,
                                            expires_at=expires_at,
                                            url=market_url
                                        )
                                        markets.append(market)
                        except Exception as e:
                            print(f"Erro ao processar evento Kalshi: {e}")
                            continue
        
        except Exception as e:
            print(f"Erro ao buscar mercados do Kalshi: {e}")
        
        return markets

