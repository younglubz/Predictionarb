"""Integração com PolyRouter - API unificada para múltiplos prediction markets"""
import httpx
from typing import List, Optional
from exchanges.base import ExchangeBase, Market
from datetime import datetime
import os
from dotenv import load_dotenv
import re

load_dotenv()


class PolyRouterExchange(ExchangeBase):
    """
    Cliente para PolyRouter - API agregada que compila dados de várias exchanges
    com padrão único, facilitando arbitragem multiplataforma.
    
    PolyRouter fornece:
    - Dados padronizados de múltiplas exchanges
    - Order books unificados
    - Liquidez agregada
    - Histórico de preços
    """
    
    def __init__(self):
        super().__init__("polyrouter")
        self.base_url = "https://api.polyrouter.io/v1"
        self.api_key = os.getenv("POLYROUTER_API_KEY")
        
        if not self.api_key:
            print("⚠️  POLYROUTER_API_KEY não encontrada no .env")
    
    def normalize_question(self, question: str) -> str:
        """Normaliza pergunta"""
        normalized = re.sub(r'[^\w\s]', '', question.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    async def fetch_markets(self) -> List[Market]:
        """
        Busca mercados agregados de múltiplas exchanges via PolyRouter
        
        PolyRouter compila dados de:
        - Polymarket
        - Kalshi
        - Manifold
        - Outras exchanges suportadas
        """
        markets = []
        
        if not self.api_key:
            return markets
        
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                # Endpoint de mercados agregados
                endpoints_to_try = [
                    "/markets",
                    "/markets/active",
                    "/aggregated/markets",
                    "/v1/markets"
                ]
                
                for endpoint in endpoints_to_try:
                    try:
                        url = f"{self.base_url}{endpoint}"
                        params = {
                            "status": "active",
                            "limit": 200,
                            "include_orderbook": True,
                            "include_liquidity": True
                        }
                        
                        response = await client.get(
                            url,
                            headers=headers,
                            params=params
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            # PolyRouter pode retornar em diferentes formatos
                            if isinstance(data, dict):
                                markets_data = data.get("data", data.get("markets", []))
                            else:
                                markets_data = data if isinstance(data, list) else []
                            
                            if not markets_data:
                                continue
                            
                            print(f"✓ PolyRouter: {len(markets_data)} mercados agregados")
                            
                            for market_data in markets_data:
                                try:
                                    parsed_markets = self._parse_market(market_data)
                                    markets.extend(parsed_markets)
                                except Exception as e:
                                    continue
                            
                            if markets:
                                break  # Sucesso, para de tentar outros endpoints
                                
                        elif response.status_code == 401:
                            print("❌ PolyRouter: API Key inválida")
                            return markets
                        elif response.status_code == 403:
                            print("❌ PolyRouter: Acesso negado - verificar plano")
                            return markets
                            
                    except httpx.TimeoutException:
                        print(f"⏱️  PolyRouter timeout no endpoint {endpoint}")
                        continue
                    except Exception as e:
                        continue
        
        except Exception as e:
            print(f"Erro ao buscar mercados do PolyRouter: {e}")
        
        return markets
    
    def _parse_market(self, market_data: dict) -> List[Market]:
        """
        Parse mercado do formato PolyRouter (padronizado)
        
        PolyRouter fornece dados em formato consistente:
        - market_id: ID único
        - question: Pergunta do mercado
        - source_exchange: Exchange de origem
        - outcomes: Lista de outcomes com preços
        - orderbook: Order book (bid/ask)
        - liquidity: Liquidez disponível
        - volume_24h: Volume 24h
        """
        markets = []
        
        try:
            # Dados básicos
            market_id = str(market_data.get("id", market_data.get("market_id", "")))
            question = market_data.get("question", market_data.get("title", ""))
            source_exchange = market_data.get("source_exchange", market_data.get("exchange", "polyrouter"))
            
            if not question:
                return markets
            
            # Outcomes
            outcomes = market_data.get("outcomes", [])
            if not outcomes:
                # Formato alternativo
                outcomes = [
                    {"name": "YES", "price": market_data.get("yes_price", market_data.get("price", 0.5))},
                    {"name": "NO", "price": market_data.get("no_price", 1 - market_data.get("price", 0.5))}
                ]
            
            # Liquidez e volume
            liquidity = float(market_data.get("liquidity", market_data.get("total_liquidity", 0)) or 0)
            volume_24h = float(market_data.get("volume_24h", market_data.get("volume24h", 0)) or 0)
            
            # Order book (se disponível)
            orderbook = market_data.get("orderbook", {})
            best_bid = float(orderbook.get("best_bid", 0) or 0) if orderbook else 0
            best_ask = float(orderbook.get("best_ask", 0) or 0) if orderbook else 0
            
            # Data de expiração
            end_date = market_data.get("end_date", market_data.get("expires_at", market_data.get("resolution_time")))
            expires_at = None
            if end_date:
                try:
                    if isinstance(end_date, (int, float)):
                        expires_at = datetime.fromtimestamp(end_date / 1000 if end_date > 1e10 else end_date)
                    else:
                        expires_at = datetime.fromisoformat(str(end_date).replace('Z', '+00:00'))
                except:
                    pass
            
            # URL do mercado
            market_url = market_data.get("url", market_data.get("link", ""))
            
            # Cria mercado para cada outcome
            for outcome_data in outcomes:
                try:
                    if isinstance(outcome_data, dict):
                        outcome_name = outcome_data.get("name", outcome_data.get("outcome", ""))
                        price = float(outcome_data.get("price", outcome_data.get("probability", 0)) or 0)
                    else:
                        continue
                    
                    # Usa preço do order book se disponível (mais preciso)
                    if best_ask > 0 and "yes" in outcome_name.lower():
                        price = best_ask
                    elif best_bid > 0 and "no" in outcome_name.lower():
                        price = 1.0 - best_bid
                    
                    # Pula mercados com certeza absoluta ou inválidos
                    if price >= 0.99 or price <= 0.01 or price <= 0:
                        continue
                    
                    # Normaliza outcome
                    outcome = "YES" if "yes" in outcome_name.lower() or outcome_name == "1" else "NO"
                    
                    market = Market(
                        exchange=f"{self.name}_{source_exchange}",  # Ex: polyrouter_polymarket
                        market_id=f"{market_id}_{outcome}",
                        question=question,
                        outcome=outcome,
                        price=price,
                        volume_24h=volume_24h,
                        liquidity=liquidity,
                        expires_at=expires_at,
                        url=market_url
                    )
                    markets.append(market)
                    
                except Exception as e:
                    continue
        
        except Exception as e:
            pass
        
        return markets
    
    async def get_orderbook(self, market_id: str) -> Optional[dict]:
        """
        Busca order book detalhado de um mercado específico
        
        Útil para:
        - Verificar liquidez real disponível
        - Calcular slippage
        - Determinar preço de execução real
        """
        if not self.api_key:
            return None
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                url = f"{self.base_url}/markets/{market_id}/orderbook"
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    return response.json()
        
        except Exception as e:
            print(f"Erro ao buscar orderbook: {e}")
        
        return None

