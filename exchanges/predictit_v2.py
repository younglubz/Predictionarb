# -*- coding: utf-8 -*-
"""
Integracao com PredictIt API
API Endpoint: https://www.predictit.org/api/marketdata/all/
"""
import httpx
from typing import List
from exchanges.base import ExchangeBase, Market
from datetime import datetime
import re


class PredictItV2Exchange(ExchangeBase):
    """
    Cliente para PredictIt API
    
    PredictIt e uma exchange regulada pela CFTC para prediction markets
    API publica disponivel em: https://www.predictit.org/api/marketdata/all/
    """
    
    def __init__(self):
        super().__init__("predictit")
        self.base_url = "https://www.predictit.org/api/marketdata"
    
    def normalize_question(self, question: str) -> str:
        """Normaliza pergunta"""
        normalized = re.sub(r'[^\w\s]', '', question.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    async def fetch_markets(self) -> List[Market]:
        """
        Busca mercados ativos do PredictIt
        
        Endpoint: GET /api/marketdata/all/
        """
        markets = []
        
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                url = f"{self.base_url}/all/"
                
                response = await client.get(
                    url,
                    headers={"Accept": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    markets_data = data.get("markets", [])
                    
                    if not markets_data:
                        return markets
                    
                    print(f"PredictIt: {len(markets_data)} mercados retornados pela API")
                    
                    for market_data in markets_data:
                        try:
                            parsed = self._parse_market(market_data)
                            if parsed:
                                markets.extend(parsed)
                        except Exception as e:
                            continue
                    
                    print(f"PredictIt: {len(markets)} mercados parseados com sucesso")
                else:
                    print(f"PredictIt API error: {response.status_code}")
        
        except Exception as e:
            print(f"Erro ao buscar mercados do PredictIt: {e}")
        
        return markets
    
    def _parse_market(self, market_data: dict) -> List[Market]:
        """Parse mercado do formato PredictIt"""
        markets = []
        
        try:
            # Dados basicos
            market_id = str(market_data.get("id", ""))
            name = market_data.get("name", "")
            short_name = market_data.get("shortName", "")
            
            # Usa shortName se disponivel, senao usa name
            question = short_name if short_name else name
            
            if not question or not market_id:
                return markets
            
            # Status
            status = market_data.get("status", "")
            if status != "Open":
                return markets
            
            # URL
            market_url = market_data.get("url", f"https://www.predictit.org/markets/detail/{market_id}")
            
            # Contratos (outcomes)
            contracts = market_data.get("contracts", [])
            
            for contract in contracts:
                try:
                    contract_id = str(contract.get("id", ""))
                    contract_name = contract.get("shortName", contract.get("name", ""))
                    contract_status = contract.get("status", "")
                    
                    if contract_status != "Open":
                        continue
                    
                    # Precos (PredictIt ja usa formato 0-1)
                    last_price = float(contract.get("lastTradePrice", 0) or 0)
                    best_buy_yes = float(contract.get("bestBuyYesCost", 0) or 0)
                    best_sell_yes = float(contract.get("bestSellYesCost", 0) or 0)
                    
                    # Usa mid price ou last price
                    if best_buy_yes > 0 and best_sell_yes > 0:
                        price = (best_buy_yes + best_sell_yes) / 2
                    else:
                        price = last_price
                    
                    # Pula mercados invalidos
                    if price <= 0:
                        continue
                    
                    # PredictIt nao fornece volume/liquidez facilmente
                    # Usa estimativas conservadoras
                    volume = 100.0  # Estimativa
                    liquidity = 200.0  # Estimativa
                    
                    # Data de expiracao
                    date_end = contract.get("dateEnd")
                    expires_at = None
                    if date_end and date_end != "NA":
                        try:
                            expires_at = datetime.fromisoformat(date_end.replace('Z', '+00:00'))
                        except:
                            pass
                    
                    # Cria pergunta completa
                    full_question = f"{question} - {contract_name}"
                    
                    # PredictIt: cada contrato tem YES e NO com preços reais
                    # Preços de NO
                    best_buy_no = float(contract.get("bestBuyNoCost", 0) or 0)
                    best_sell_no = float(contract.get("bestSellNoCost", 0) or 0)
                    
                    # Calcula mid price do NO
                    if best_buy_no > 0 and best_sell_no > 0:
                        no_price = (best_buy_no + best_sell_no) / 2
                    elif best_buy_no > 0:
                        no_price = best_buy_no
                    elif best_sell_no > 0:
                        no_price = best_sell_no
                    else:
                        no_price = 1.0 - price  # Fallback
                    
                    # YES
                    market_yes = Market(
                        exchange=self.name,
                        market_id=f"{market_id}_{contract_id}_YES",
                        question=full_question,
                        outcome="YES",
                        price=price,
                        volume_24h=volume,
                        liquidity=liquidity,
                        expires_at=expires_at,
                        url=market_url
                    )
                    markets.append(market_yes)
                    
                    # NO (com preço real da API)
                    if no_price > 0 and no_price < 1.0:
                        market_no = Market(
                            exchange=self.name,
                            market_id=f"{market_id}_{contract_id}_NO",
                            question=full_question,
                            outcome="NO",
                            price=no_price,
                            volume_24h=volume,
                            liquidity=liquidity,
                            expires_at=expires_at,
                            url=market_url
                        )
                        markets.append(market_no)
                    
                except Exception as e:
                    continue
        
        except Exception as e:
            pass
        
        return markets

