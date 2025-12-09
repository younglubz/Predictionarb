"""Integração com Omen (Gnosis) - Prediction markets descentralizado"""
import httpx
from typing import List
from exchanges.base import ExchangeBase, Market
from datetime import datetime
import re


class OmenExchange(ExchangeBase):
    """Cliente para Omen (Gnosis Chain)"""
    
    def __init__(self):
        super().__init__("omen")
        # Omen usa The Graph na Gnosis Chain
        self.base_url = "https://api.thegraph.com/subgraphs/name/protofire/omen-xdai"
        
    def normalize_question(self, question: str) -> str:
        """Normaliza pergunta"""
        normalized = re.sub(r'[^\w\s]', '', question.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    async def fetch_markets(self) -> List[Market]:
        """Busca mercados ativos do Omen"""
        markets = []
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # GraphQL query para mercados ativos
                query = """
                {
                  fixedProductMarketMakers(
                    first: 100
                    orderBy: creationTimestamp
                    orderDirection: desc
                    where: {
                      answerFinalizedTimestamp: null
                    }
                  ) {
                    id
                    question {
                      id
                      title
                      outcomes
                      answerFinalizedTimestamp
                    }
                    outcomeTokenAmounts
                    collateralVolume
                    liquidityParameter
                    openingTimestamp
                  }
                }
                """
                
                response = await client.post(
                    self.base_url,
                    json={"query": query},
                    headers={"Content-Type": "application/json"},
                    timeout=15.0
                )
                
                if response.status_code != 200:
                    return markets
                
                data = response.json()
                fpmms = data.get("data", {}).get("fixedProductMarketMakers", [])
                
                for fpmm in fpmms:
                    try:
                        market_id = fpmm.get("id", "")
                        question_data = fpmm.get("question", {})
                        
                        if not question_data:
                            continue
                        
                        question = question_data.get("title", "")
                        outcomes = question_data.get("outcomes", [])
                        
                        if not question or not outcomes:
                            continue
                        
                        # Volumes e liquidez
                        volume = float(fpmm.get("collateralVolume", 0) or 0)
                        liquidity = float(fpmm.get("liquidityParameter", 0) or 0)
                        
                        # Amounts para cada outcome (usado para calcular probabilidade)
                        amounts = fpmm.get("outcomeTokenAmounts", [])
                        
                        # Cria mercado para cada outcome
                        for i, outcome_name in enumerate(outcomes):
                            try:
                                # Calcula probabilidade baseada nos amounts
                                if amounts and len(amounts) > i:
                                    total = sum(float(a) for a in amounts if a)
                                    if total > 0:
                                        price = float(amounts[i]) / total
                                    else:
                                        price = 1.0 / len(outcomes)
                                else:
                                    price = 1.0 / len(outcomes)
                                
                                # Pula mercados com certeza absoluta
                                if price >= 0.99 or price <= 0.01:
                                    continue
                                
                                # Normaliza outcome
                                outcome = "YES" if "yes" in outcome_name.lower() else "NO"
                                
                                market = Market(
                                    exchange=self.name,
                                    market_id=f"{market_id}_{i}",
                                    question=question,
                                    outcome=outcome,
                                    price=price,
                                    volume_24h=volume / 7,  # Estimativa diária
                                    liquidity=liquidity,
                                    expires_at=None,  # Omen não expõe facilmente
                                    url=f"https://omen.eth.limo/#/{market_id}"
                                )
                                markets.append(market)
                            except Exception as e:
                                continue
                    except Exception as e:
                        continue
        
        except Exception as e:
            print(f"Erro ao buscar mercados do Omen: {e}")
        
        return markets

