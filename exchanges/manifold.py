"""Integração com Manifold Markets"""
import httpx
from typing import List
from exchanges.base import ExchangeBase, Market
from datetime import datetime
import re


class ManifoldExchange(ExchangeBase):
    """Cliente para Manifold Markets API"""
    
    def __init__(self):
        super().__init__("manifold")
        self.base_url = "https://api.manifold.markets/v0"
    
    def normalize_question(self, question: str) -> str:
        """Normaliza pergunta"""
        normalized = re.sub(r'[^\w\s]', '', question.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    async def fetch_markets(self) -> List[Market]:
        """Busca mercados ativos do Manifold"""
        markets = []
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Manifold API - busca mercados
                url = f"{self.base_url}/markets"
                params = {
                    "limit": 100
                }
                
                response = await client.get(
                    url,
                    params=params,
                    headers={"Accept": "application/json"}
                )
                print(f"Manifold API Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    # Manifold retorna lista direta
                    markets_data = data if isinstance(data, list) else []
                    
                    if not markets_data:
                        return markets
                    
                    for market_data in markets_data:
                        try:
                            # Pula mercados resolvidos
                            if market_data.get("isResolved", False):
                                continue
                            
                            market_id = str(market_data.get("id", ""))
                            question = market_data.get("question", "")
                            
                            if not question:
                                continue
                            
                            # Manifold tem probabilidade (0-1)
                            # Pode ser None, então trata isso
                            prob_value = market_data.get("probability")
                            if prob_value is None:
                                # Se não tem probabilidade, usa 0.5 como padrão
                                probability = 0.5
                            else:
                                probability = float(prob_value)
                            
                            # Volume e liquidez
                            volume_24h = float(market_data.get("volume24Hours", 0) or 0)
                            liquidity = float(market_data.get("liquidity", max(volume_24h * 0.1, 100)) or 100)
                            
                            # Data de resolução
                            resolution_time = market_data.get("resolutionTime")
                            creator = market_data.get("creatorUsername", "")
                            slug = market_data.get("slug", market_id)
                            market_url = market_data.get("url") or f"https://manifold.markets/{creator}/{slug}"
                            
                            expires_at = None
                            if resolution_time:
                                try:
                                    if isinstance(resolution_time, (int, float)):
                                        expires_at = datetime.fromtimestamp(resolution_time / 1000)
                                    else:
                                        expires_at = datetime.fromisoformat(str(resolution_time).replace('Z', '+00:00'))
                                except:
                                    pass
                            
                            # Pula mercados com certeza absoluta (já resolvidos)
                            if probability >= 0.99 or probability <= 0.01:
                                continue
                            
                            # Manifold tem apenas probabilidade (YES)
                            # Criamos um mercado YES
                            if question:
                                market = Market(
                                    exchange=self.name,
                                    market_id=f"{market_id}_YES",
                                    question=question,
                                    outcome="YES",
                                    price=probability,
                                    volume_24h=volume_24h,
                                    liquidity=liquidity,
                                    expires_at=expires_at,
                                    url=market_url
                                )
                                markets.append(market)
                                
                                # Também criamos um NO (1 - probability)
                                market_no = Market(
                                    exchange=self.name,
                                    market_id=f"{market_id}_NO",
                                    question=question,
                                    outcome="NO",
                                    price=1.0 - probability,
                                    volume_24h=volume_24h,
                                    liquidity=liquidity,
                                    expires_at=expires_at,
                                    url=market_url
                                )
                                markets.append(market_no)
                        except Exception as e:
                            # Erro silencioso - continua processando outros mercados
                            continue
        
        except Exception as e:
            print(f"Erro ao buscar mercados do Manifold: {e}")
        
        return markets

