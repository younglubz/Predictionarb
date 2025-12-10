"""Integração com Polymarket"""
import httpx
import asyncio
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
        """Busca mercados ativos do Polymarket usando API real com paginação"""
        markets = []
        max_pages = 5  # Limita a 5 páginas (5000 mercados) para não demorar muito
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Polymarket API v2 - busca mercados ativos
                url = f"{self.base_url}/markets"
                
                # Busca múltiplas páginas usando paginação
                cursor = None
                page = 0
                
                while page < max_pages:
                    params = {
                        "limit": 1000,  # Aumentado de 100 para 1000 (máximo da API)
                        "sort": "newest"  # Ordena por mais recentes (mercados ativos)
                    }
                    
                    # Não filtra por active na query - filtra depois para ter mais controle
                    
                    if cursor:
                        params["cursor"] = cursor
                    
                    response = await client.get(
                        url,
                        params=params,
                        headers={"Accept": "application/json"}
                    )
                    
                    if response.status_code != 200:
                        print(f"Polymarket: Erro na página {page + 1} - Status {response.status_code}")
                        break
                    
                    data = response.json()
                    # Polymarket retorna {"data": [...], "next_cursor": ..., "count": ...}
                    if isinstance(data, dict) and "data" in data:
                        markets_data = data["data"]
                        cursor = data.get("next_cursor")
                    elif isinstance(data, list):
                        markets_data = data
                        cursor = None
                    else:
                        markets_data = []
                        cursor = None
                    
                    if not markets_data:
                        break
                    
                    print(f"Polymarket: Página {page + 1} - {len(markets_data)} mercados")
                    
                    for market_data in markets_data:
                            try:
                                # Filtros para mercados válidos
                                # 1. Não deve estar arquivado (arquivados são definitivamente inativos)
                                if market_data.get("archived", False):
                                    continue
                                
                                # 2. Preferência por não fechados, mas aceita fechados se tiverem preços válidos
                                # (alguns mercados fechados ainda podem ter dados úteis)
                                is_closed = market_data.get("closed", False)
                                
                                # Nota: A API retorna principalmente mercados fechados quando ordenada por volume.
                                # Vamos aceitar mercados fechados se tiverem preços válidos, mas priorizar não-fechados.
                                
                                market_id = str(market_data.get("condition_id", market_data.get("id", "")))
                                question = market_data.get("question", "")
                                
                                if not question:
                                    continue
                                
                                # Polymarket usa "tokens" (não "outcomes")
                                # Cada token representa um outcome (Yes/No)
                                tokens_data = market_data.get("tokens", [])
                                if not tokens_data:
                                    # Fallback para outcomes se tokens não existir
                                    tokens_data = market_data.get("outcomes", [])
                                
                                if not tokens_data:
                                    continue
                                
                                volume = float(market_data.get("volume", 0) or 0)
                                liquidity = float(market_data.get("liquidity", 0) or 0)
                                end_date = market_data.get("endDate") or market_data.get("end_date") or market_data.get("end_date_iso")
                                
                                # Polymarket URL: usa slug se disponível, senão usa condition_id
                                slug = market_data.get("slug") or market_data.get("condition_id") or market_id
                                market_url = market_data.get("url") or f"https://polymarket.com/event/{slug}"
                                
                                # Garante que a URL não está vazia
                                if not market_url or market_url == "https://polymarket.com/event/":
                                    market_url = f"https://polymarket.com/markets/{market_id}"
                                
                                # Para mercados Yes/No, cria apenas um mercado (Yes)
                                # Para mercados com múltiplos outcomes, cria um para cada
                                is_yes_no_market = False
                                
                                # Verifica se é mercado Yes/No
                                outcome_names = []
                                if tokens_data:
                                    for token in tokens_data:
                                        if isinstance(token, dict):
                                            outcome_name = token.get("outcome", token.get("name", ""))
                                            if outcome_name:
                                                outcome_names.append(outcome_name.lower())
                                
                                # Se tem "yes" e "no", é mercado Yes/No
                                if "yes" in outcome_names and "no" in outcome_names:
                                    is_yes_no_market = True
                                
                                # Cria mercado para cada token (outcome)
                                for token_data in tokens_data:
                                    if isinstance(token_data, dict):
                                        # Token tem estrutura: {"outcome": "Yes", "price": 0.65, ...}
                                        outcome_name = token_data.get("outcome", token_data.get("name", ""))
                                        
                                        # Preço pode estar em diferentes campos
                                        price = float(
                                            token_data.get("price") or 
                                            token_data.get("lastPrice") or 
                                            token_data.get("last_price") or 
                                            0
                                        )
                                        
                                        # Se price é exatamente 0 ou 1, mercado já foi resolvido
                                        # Mas se o mercado está fechado E o preço é 0 ou 1, definitivamente resolvido
                                        if is_closed and (price == 0.0 or price == 1.0):
                                            continue
                                        
                                        # Para mercados não fechados, aceita qualquer preço válido
                                        # Para mercados fechados, só aceita se preço não for 0 ou 1
                                        if not is_closed and (price == 0.0 or price == 1.0):
                                            continue
                                    else:
                                        # Formato alternativo (string) - raro
                                        outcome_name = str(token_data)
                                        price = float(market_data.get("price", 0) or 0)
                                        
                                        if price == 0.0 or price == 1.0:
                                            continue
                                    
                                    # Normaliza outcome para YES/NO
                                    # Polymarket usa "Yes" e "No" (com maiúscula)
                                    if not outcome_name:
                                        continue
                                    
                                    # Para mercados Yes/No, só processa o "Yes" (o "No" é 1 - Yes)
                                    if is_yes_no_market:
                                        if "no" in outcome_name.lower():
                                            continue  # Pula "No", processa apenas "Yes"
                                        outcome = "YES"
                                    else:
                                        # Para outros tipos de mercado, tenta identificar
                                        outcome = "YES" if "yes" in outcome_name.lower() else "NO"
                                    
                                    expires_at = None
                                    if end_date:
                                        try:
                                            if isinstance(end_date, str):
                                                # Tenta diferentes formatos
                                                try:
                                                    expires_at = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                                                except:
                                                    # Formato alternativo
                                                    expires_at = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                                            else:
                                                expires_at = datetime.fromtimestamp(end_date / 1000)
                                        except:
                                            pass
                                    
                                    # Valida se tem dados mínimos e preço válido (entre 0 e 1, não exatamente 0 ou 1)
                                    # IMPORTANTE: Filtra mercados com preços extremos que são claramente resolvidos
                                    # Preços muito baixos (< 0.005) ou muito altos (> 0.995) geralmente são mercados resolvidos
                                    # Aceita mercados com liquidez >= 0 (pode ser baixa, mas não zero absoluto se o preço for extremo)
                                    # Se o preço está entre 0.005 e 0.995, aceita mesmo com liquidez baixa (pode ser mercado novo)
                                    if (question and outcome_name and
                                        ((0.005 <= price <= 0.995) or  # Preço razoável, aceita qualquer liquidez
                                         (0.01 <= price <= 0.99 and liquidity > 0))):  # Preço extremo só se tiver liquidez
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
                                # Silencia erros individuais para não poluir logs
                                continue
                    
                    # Se não há mais páginas, para
                    if not cursor:
                        break
                    
                    page += 1
                    
                    # Pequena pausa entre requisições para não sobrecarregar API
                    await asyncio.sleep(0.5)
        
        except Exception as e:
            print(f"Erro ao buscar mercados do Polymarket: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"Polymarket: Total de {len(markets)} mercados encontrados")
        return markets

