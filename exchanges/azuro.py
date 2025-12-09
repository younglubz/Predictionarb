"""Integração com Azuro - Prediction markets focado em esportes"""
import httpx
from typing import List
from exchanges.base import ExchangeBase, Market
from datetime import datetime
import re


class AzuroExchange(ExchangeBase):
    """Cliente para Azuro API"""
    
    def __init__(self):
        super().__init__("azuro")
        # Azuro usa The Graph para queries
        self.base_url = "https://thegraph.azuro.org/subgraphs/name/azuro-protocol/azuro-api-polygon-v3"
        
    def normalize_question(self, question: str) -> str:
        """Normaliza pergunta"""
        normalized = re.sub(r'[^\w\s]', '', question.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    async def fetch_markets(self) -> List[Market]:
        """Busca mercados ativos do Azuro"""
        markets = []
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # GraphQL query para buscar jogos ativos
                query = """
                {
                  games(
                    first: 100
                    where: {
                      status: Paused_or_Created
                      startsAt_gt: "1735689600"
                    }
                    orderBy: startsAt
                    orderDirection: asc
                  ) {
                    id
                    sport {
                      name
                    }
                    league {
                      name
                    }
                    participants {
                      name
                    }
                    startsAt
                    conditions {
                      id
                      outcomes {
                        id
                        odds
                      }
                    }
                  }
                }
                """
                
                response = await client.post(
                    self.base_url,
                    json={"query": query},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    return markets
                
                data = response.json()
                games = data.get("data", {}).get("games", [])
                
                for game in games:
                    try:
                        game_id = game.get("id", "")
                        sport = game.get("sport", {}).get("name", "")
                        league = game.get("league", {}).get("name", "")
                        participants = game.get("participants", [])
                        
                        if len(participants) < 2:
                            continue
                        
                        team1 = participants[0].get("name", "")
                        team2 = participants[1].get("name", "")
                        question = f"{sport}: {team1} vs {team2} ({league})"
                        
                        # Data do jogo
                        starts_at = game.get("startsAt")
                        expires_at = None
                        if starts_at:
                            try:
                                expires_at = datetime.fromtimestamp(int(starts_at))
                            except:
                                pass
                        
                        # Condições (mercados)
                        conditions = game.get("conditions", [])
                        for condition in conditions:
                            outcomes = condition.get("outcomes", [])
                            
                            for outcome in outcomes:
                                try:
                                    odds = float(outcome.get("odds", 0))
                                    if odds <= 0:
                                        continue
                                    
                                    # Converte odds para probabilidade
                                    # Odds no Azuro são em formato decimal
                                    price = 1.0 / odds if odds > 0 else 0.5
                                    
                                    # Pula mercados resolvidos
                                    if price >= 0.99 or price <= 0.01:
                                        continue
                                    
                                    outcome_id = outcome.get("id", "")
                                    
                                    # Determina outcome (simplificado)
                                    outcome_name = "YES" if "1" in outcome_id or "home" in outcome_id.lower() else "NO"
                                    
                                    market = Market(
                                        exchange=self.name,
                                        market_id=f"{game_id}_{outcome_id}",
                                        question=question,
                                        outcome=outcome_name,
                                        price=price,
                                        volume_24h=0,  # Azuro não expõe volume facilmente
                                        liquidity=1000,  # Estimativa conservadora
                                        expires_at=expires_at,
                                        url=f"https://azuro.org/events/{game_id}"
                                    )
                                    markets.append(market)
                                except Exception as e:
                                    continue
                    except Exception as e:
                        continue
        
        except Exception as e:
            print(f"Erro ao buscar mercados do Azuro: {e}")
        
        return markets

