"""Integração com PredictIt"""
import httpx
from typing import List
from exchanges.base import ExchangeBase, Market
from datetime import datetime
import re


class PredictItExchange(ExchangeBase):
    """Cliente para PredictIt API"""
    
    def __init__(self):
        super().__init__("predictit")
        self.base_url = "https://www.predictit.org/api"
    
    def normalize_question(self, question: str) -> str:
        """Normaliza pergunta"""
        normalized = re.sub(r'[^\w\s]', '', question.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    async def fetch_markets(self) -> List[Market]:
        """Busca mercados ativos do PredictIt"""
        markets = []
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # PredictIt pode precisar de headers específicos
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/json"
                }
                response = await client.get(
                    f"{self.base_url}/Market/GetAllMarkets",
                    headers=headers
                )
                if response.status_code == 200:
                    data = response.json()
                    # Verifica se é lista ou dict
                    if isinstance(data, dict):
                        # Pode ter estrutura diferente
                        markets_list = data.get("markets", data.get("data", []))
                    else:
                        markets_list = data if isinstance(data, list) else []
                    
                    for market_data in markets_list:
                            market_id = str(market_data.get("Id", ""))
                            question = market_data.get("Name", "")
                            contracts = market_data.get("Contracts", [])
                            volume = float(market_data.get("Volume", 0))
                            end_date = market_data.get("DateEnd")
                            
                            expires_at = None
                            if end_date:
                                try:
                                    expires_at = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                                except:
                                    pass
                            
                            # PredictIt tem múltiplos contratos por mercado
                            for contract in contracts:
                                contract_id = str(contract.get("Id", ""))
                                outcome = contract.get("Name", "")
                                price = float(contract.get("LastTradePrice", 0))
                                
                                # Normaliza para YES/NO quando possível
                                outcome_type = "YES" if "yes" in outcome.lower() else "NO"
                                
                                market = Market(
                                    exchange=self.name,
                                    market_id=f"{market_id}_{contract_id}",
                                    question=question,
                                    outcome=outcome_type,
                                    price=price,
                                    volume_24h=volume,
                                    liquidity=volume * 0.1,  # Estimativa
                                    expires_at=expires_at,
                                    url=f"https://www.predictit.org/markets/detail/{market_id}"
                                )
                                markets.append(market)
        
        except Exception as e:
            print(f"Erro ao buscar mercados do PredictIt: {e}")
        
        return markets
