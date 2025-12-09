"""Integração com Seer - Prediction markets na Gnosis Chain"""
import httpx
from typing import List
from exchanges.base import ExchangeBase, Market
from datetime import datetime
import re


class SeerExchange(ExchangeBase):
    """Cliente para Seer"""
    
    def __init__(self):
        super().__init__("seer")
        # API pública do Seer
        self.base_url = "https://api.seer.pm/v1"
        
    def normalize_question(self, question: str) -> str:
        """Normaliza pergunta"""
        normalized = re.sub(r'[^\w\s]', '', question.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    async def fetch_markets(self) -> List[Market]:
        """Busca mercados ativos do Seer"""
        markets = []
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Tenta diferentes endpoints
                endpoints = ["/markets", "/markets/active"]
                
                for endpoint in endpoints:
                    try:
                        response = await client.get(
                            f"{self.base_url}{endpoint}",
                            params={"status": "open", "limit": 100},
                            headers={"Accept": "application/json"}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            markets_data = data if isinstance(data, list) else data.get("markets", [])
                            
                            for market_data in markets_data:
                                try:
                                    market_id = str(market_data.get("id", ""))
                                    question = market_data.get("question", market_data.get("title", ""))
                                    
                                    if not question:
                                        continue
                                    
                                    # Outcomes
                                    outcomes = market_data.get("outcomes", [])
                                    
                                    for outcome_data in outcomes:
                                        if isinstance(outcome_data, dict):
                                            outcome_name = outcome_data.get("name", "")
                                            price = float(outcome_data.get("price", outcome_data.get("probability", 0.5)) or 0.5)
                                        else:
                                            continue
                                        
                                        # Pula mercados resolvidos
                                        if price >= 0.99 or price <= 0.01:
                                            continue
                                        
                                        volume = float(market_data.get("volume", 0) or 0)
                                        liquidity = float(market_data.get("liquidity", 0) or 0)
                                        
                                        outcome = "YES" if "yes" in outcome_name.lower() else "NO"
                                        
                                        market = Market(
                                            exchange=self.name,
                                            market_id=f"{market_id}_{outcome_name}",
                                            question=question,
                                            outcome=outcome,
                                            price=price,
                                            volume_24h=volume,
                                            liquidity=liquidity,
                                            expires_at=None,
                                            url=f"https://seer.pm/market/{market_id}"
                                        )
                                        markets.append(market)
                                except Exception as e:
                                    continue
                            
                            if markets:
                                break
                    except Exception as e:
                        continue
        
        except Exception as e:
            print(f"Erro ao buscar mercados do Seer: {e}")
        
        return markets

