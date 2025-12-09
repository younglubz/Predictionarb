"""Integração com FinFeedAPI - API agregada de prediction markets"""
import httpx
from typing import List, Dict, Optional
from exchanges.base import ExchangeBase, Market
from datetime import datetime
import re


class FinFeedExchange(ExchangeBase):
    """Cliente para FinFeedAPI - agrega dados de múltiplas exchanges"""
    
    def __init__(self):
        super().__init__("finfeed")
        # FinFeedAPI - API agregada
        self.base_url = "https://api.finfeed.com/v1"
        # Alternativa: usar endpoint público se disponível
        # Nota: Pode precisar de API key
        self.api_key = None  # Configurar via .env se necessário
    
    def normalize_question(self, question: str) -> str:
        """Normaliza pergunta"""
        normalized = re.sub(r'[^\w\s]', '', question.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    async def fetch_markets(self) -> List[Market]:
        """Busca mercados ativos via FinFeedAPI"""
        markets = []
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                headers = {"Accept": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                # Tenta diferentes endpoints
                endpoints = [
                    "/markets",
                    "/prediction-markets",
                    "/markets/active"
                ]
                
                for endpoint in endpoints:
                    try:
                        url = f"{self.base_url}{endpoint}"
                        params = {"limit": 100, "active": "true"}
                        
                        response = await client.get(url, params=params, headers=headers)
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            # FinFeedAPI pode retornar em diferentes formatos
                            if isinstance(data, dict):
                                markets_data = data.get("data", data.get("markets", []))
                            else:
                                markets_data = data if isinstance(data, list) else []
                            
                            if markets_data:
                                for market_data in markets_data:
                                    try:
                                        market = self._parse_market(market_data)
                                        if market:
                                            markets.append(market)
                                    except Exception as e:
                                        print(f"Erro ao processar mercado FinFeed: {e}")
                                        continue
                            
                            if markets:
                                break  # Se encontrou mercados, para de tentar outros endpoints
                    except Exception as e:
                        continue
                
                # Se não encontrou nada, tenta buscar de exchanges específicas via FinFeed
                if not markets:
                    # FinFeed pode ter endpoints por exchange
                    exchanges = ["polymarket", "myriad", "kalshi", "manifold"]
                    for exchange_name in exchanges:
                        try:
                            url = f"{self.base_url}/markets/{exchange_name}"
                            response = await client.get(url, params={"limit": 50}, headers=headers)
                            if response.status_code == 200:
                                data = response.json()
                                markets_list = data.get("data", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
                                for market_data in markets_list:
                                    try:
                                        market = self._parse_market(market_data, exchange_name)
                                        if market:
                                            markets.append(market)
                                    except:
                                        continue
                        except:
                            continue
        
        except Exception as e:
            print(f"Erro ao buscar mercados do FinFeedAPI: {e}")
        
        return markets
    
    def _parse_market(self, market_data: Dict, exchange_override: Optional[str] = None) -> Optional[Market]:
        """Parse mercado do formato FinFeedAPI"""
        try:
            # FinFeedAPI pode ter estrutura padronizada
            market_id = str(market_data.get("id", market_data.get("market_id", "")))
            question = market_data.get("question", market_data.get("title", market_data.get("name", "")))
            
            if not question:
                return None
            
            # Exchange de origem
            exchange = exchange_override or market_data.get("exchange", market_data.get("platform", "finfeed"))
            
            # Preços e outcomes
            outcomes = market_data.get("outcomes", [])
            if not outcomes:
                # Tenta formato alternativo
                price = float(market_data.get("price", market_data.get("probability", 0)) or 0)
                if price > 0:
                    outcomes = [{"outcome": "YES", "price": price}]
            
            # Volume e liquidez
            volume_24h = float(market_data.get("volume_24h", market_data.get("volume24h", market_data.get("volume", 0))) or 0)
            liquidity = float(market_data.get("liquidity", market_data.get("total_liquidity", volume_24h * 0.1)) or 0)
            
            # Data de expiração
            end_date = market_data.get("end_date", market_data.get("expires_at", market_data.get("resolution_time")))
            market_url = market_data.get("url", market_data.get("link", ""))
            
            expires_at = None
            if end_date:
                try:
                    if isinstance(end_date, (int, float)):
                        expires_at = datetime.fromtimestamp(end_date / 1000 if end_date > 1e10 else end_date)
                    else:
                        expires_at = datetime.fromisoformat(str(end_date).replace('Z', '+00:00'))
                except:
                    pass
            
            markets_list = []
            
            # Cria mercado para cada outcome
            for outcome_data in outcomes:
                if isinstance(outcome_data, dict):
                    outcome_name = outcome_data.get("outcome", outcome_data.get("name", ""))
                    price = float(outcome_data.get("price", outcome_data.get("probability", 0)) or 0)
                else:
                    outcome_name = str(outcome_data)
                    price = float(market_data.get("price", 0) or 0)
                
                # Normaliza outcome
                outcome = "YES" if "yes" in outcome_name.lower() or outcome_name.lower() == "1" else "NO"
                
                if price > 0 and question:
                    market = Market(
                        exchange=exchange,
                        market_id=f"{market_id}_{outcome}",
                        question=question,
                        outcome=outcome,
                        price=price,
                        volume_24h=volume_24h,
                        liquidity=liquidity,
                        expires_at=expires_at,
                        url=market_url
                    )
                    markets_list.append(market)
            
            return markets_list[0] if markets_list else None
            
        except Exception as e:
            print(f"Erro ao parse mercado FinFeed: {e}")
            return None

