"""Integração com Polymarket"""
import httpx
from typing import List
from exchanges.base import ExchangeBase, Market
from datetime import datetime
import re


class PolymarketExchange(ExchangeBase):
    """Cliente para Polymarket API"""
    
    def __init__(self):
        super().__init__("polymarket")
        self.base_url = "https://clob.polymarket.com"
    
    def normalize_question(self, question: str) -> str:
        """Normaliza pergunta removendo caracteres especiais e lowercase"""
        # Remove caracteres especiais, mantém apenas alfanuméricos e espaços
        normalized = re.sub(r'[^\w\s]', '', question.lower())
        # Remove espaços múltiplos
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    async def fetch_markets(self) -> List[Market]:
        """Busca mercados ativos do Polymarket usando API real"""
        markets = []
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Polymarket API v2 - busca mercados ativos
                url = f"{self.base_url}/markets"
                params = {
                    "active": "true",
                    "limit": 100,
                    "sort": "volume"
                }
                
                response = await client.get(
                    url,
                    params=params,
                    headers={"Accept": "application/json"}
                )
                if response.status_code == 200:
                    data = response.json()
                    # Polymarket retorna {"data": [...], "next_cursor": ..., "count": ...}
                    if isinstance(data, dict) and "data" in data:
                        markets_data = data["data"]
                    elif isinstance(data, list):
                        markets_data = data
                    else:
                        markets_data = []
                    
                    for market_data in markets_data:
                            try:
                                market_id = str(market_data.get("id", ""))
                                question = market_data.get("question", "")
                                
                                # Polymarket tem outcomes como "Yes" e "No"
                                outcomes_data = market_data.get("outcomes", [])
                                if not outcomes_data:
                                    # Tenta buscar de outra estrutura
                                    outcomes_data = market_data.get("tokens", [])
                                
                                volume = float(market_data.get("volume", 0) or 0)
                                liquidity = float(market_data.get("liquidity", 0) or 0)
                                end_date = market_data.get("endDate") or market_data.get("end_date")
                                
                                # Polymarket URL: usa slug se disponível, senão usa condition_id
                                slug = market_data.get("slug") or market_data.get("condition_id") or market_id
                                market_url = market_data.get("url") or f"https://polymarket.com/event/{slug}"
                                
                                # Garante que a URL não está vazia
                                if not market_url or market_url == "https://polymarket.com/event/":
                                    market_url = f"https://polymarket.com/markets/{market_id}"
                                
                                # Cria mercado para cada outcome
                                for outcome_data in outcomes_data:
                                    if isinstance(outcome_data, dict):
                                        outcome_name = outcome_data.get("outcome", outcome_data.get("name", ""))
                                        price = float(outcome_data.get("price", outcome_data.get("lastPrice", 0)) or 0)
                                    else:
                                        # Formato alternativo
                                        outcome_name = str(outcome_data)
                                        price = float(market_data.get("price", 0) or 0)
                                    
                                    # Normaliza outcome para YES/NO
                                    outcome = "YES" if "yes" in outcome_name.lower() else "NO"
                                    
                                    expires_at = None
                                    if end_date:
                                        try:
                                            if isinstance(end_date, str):
                                                expires_at = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                                            else:
                                                expires_at = datetime.fromtimestamp(end_date / 1000)
                                        except:
                                            pass
                                    
                                    # Pula mercados resolvidos ou com certeza absoluta
                                    if price >= 0.99 or price <= 0.01:
                                        continue
                                    
                                    if price > 0 and question:
                                        market = Market(
                                            exchange=self.name,
                                            market_id=f"{market_id}_{outcome}",
                                            question=question,
                                            outcome=outcome,
                                            price=price,
                                            volume_24h=volume,
                                            liquidity=liquidity,
                                            expires_at=expires_at,
                                            url=market_url
                                        )
                                        markets.append(market)
                            except Exception as e:
                                print(f"Erro ao processar mercado Polymarket: {e}")
                                continue
        
        except Exception as e:
            print(f"Erro ao buscar mercados do Polymarket: {e}")
        
        return markets

