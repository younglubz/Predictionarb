# -*- coding: utf-8 -*-
"""
Integracao com Kalshi API v2 - Oficial
Documentacao: https://docs.kalshi.com/welcome

Kalshi e uma exchange regulada pela CFTC para prediction markets
"""
import httpx
from typing import List, Optional
from exchanges.base import ExchangeBase, Market
from datetime import datetime
import os
from dotenv import load_dotenv
import re

load_dotenv()


class KalshiV2Exchange(ExchangeBase):
    """
    Cliente para Kalshi Exchange API
    
    Recursos:
    - Dados de mercado em tempo real
    - Order books detalhados
    - Execucao de trades (via API key)
    - WebSocket para streaming
    
    Documentacao: https://docs.kalshi.com/
    """
    
    def __init__(self):
        super().__init__("kalshi")
        # API de producao
        self.base_url = "https://api.elections.kalshi.com/trade-api/v2"
        # Demo para testes
        self.demo_url = "https://demo-api.kalshi.co/trade-api/v2"
        
        # Usa demo por padrao (mais seguro para testes)
        self.use_demo = os.getenv("KALSHI_USE_DEMO", "true").lower() == "true"
        self.api_url = self.demo_url if self.use_demo else self.base_url
        
        # API credentials (opcional para dados publicos)
        self.api_key = os.getenv("KALSHI_API_KEY")
        self.api_secret = os.getenv("KALSHI_API_SECRET")
        
        self.session_token = None
    
    def normalize_question(self, question: str) -> str:
        """Normaliza pergunta"""
        normalized = re.sub(r'[^\w\s]', '', question.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    async def login(self) -> bool:
        """
        Faz login na API Kalshi (necessario para trading)
        Dados publicos nao precisam de autenticacao
        """
        if not self.api_key or not self.api_secret:
            # Sem credenciais - modo somente leitura (OK para arbitragem)
            return False
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.api_url}/login",
                    json={
                        "email": self.api_key,
                        "password": self.api_secret
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.session_token = data.get("token")
                    return True
        except Exception as e:
            print(f"Kalshi login error: {e}")
        
        return False
    
    def _get_headers(self) -> dict:
        """Retorna headers para requisicoes"""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        if self.session_token:
            headers["Authorization"] = f"Bearer {self.session_token}"
        
        return headers
    
    async def fetch_markets(self) -> List[Market]:
        """
        Busca mercados ativos da Kalshi
        
        Endpoint: GET /markets
        Docs: https://docs.kalshi.com/api-reference/markets
        """
        markets = []
        
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                # Endpoint de mercados
                url = f"{self.api_url}/markets"
                
                params = {
                    "limit": 200,
                    "status": "open",  # Apenas mercados abertos
                }
                
                response = await client.get(
                    url,
                    params=params,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    markets_data = data.get("markets", [])
                    
                    if not markets_data:
                        return markets
                    
                    print(f"Kalshi: {len(markets_data)} mercados retornados pela API")
                    
                    for market_data in markets_data:
                        try:
                            parsed = self._parse_market(market_data, client)
                            if parsed:
                                markets.extend(parsed)
                        except Exception as e:
                            # Silencia erros de parsing individual
                            continue
                    
                    print(f"Kalshi: {len(markets)} mercados parseados com sucesso")
                
                elif response.status_code == 401:
                    print("Kalshi: Sem autenticacao (usando dados publicos)")
                    # Tenta endpoint publico alternativo
                    return await self._fetch_public_markets(client)
                else:
                    print(f"Kalshi API error: {response.status_code}")
        
        except Exception as e:
            print(f"Erro ao buscar mercados da Kalshi: {e}")
        
        return markets
    
    async def _fetch_public_markets(self, client: httpx.AsyncClient) -> List[Market]:
        """Tenta buscar mercados via endpoint publico"""
        markets = []
        
        try:
            # Endpoint publico de series (categorias)
            url = f"{self.api_url}/series"
            response = await client.get(url, params={"limit": 50})
            
            if response.status_code == 200:
                data = response.json()
                series = data.get("series", [])
                
                # Para cada serie, busca seus mercados
                for serie in series[:10]:  # Limita a 10 series
                    serie_ticker = serie.get("ticker")
                    if not serie_ticker:
                        continue
                    
                    # Busca mercados da serie
                    markets_url = f"{self.api_url}/series/{serie_ticker}/markets"
                    markets_response = await client.get(markets_url)
                    
                    if markets_response.status_code == 200:
                        markets_data = markets_response.json().get("markets", [])
                        for market_data in markets_data:
                            parsed = self._parse_market(market_data, client)
                            if parsed:
                                markets.extend(parsed)
        except Exception as e:
            print(f"Erro ao buscar mercados publicos: {e}")
        
        return markets
    
    def _parse_market(self, market_data: dict, client: httpx.AsyncClient = None) -> List[Market]:
        """Parse mercado do formato Kalshi"""
        markets = []
        
        try:
            # Dados basicos
            ticker = market_data.get("ticker", "")
            title = market_data.get("title", "")
            subtitle = market_data.get("subtitle", "")
            
            # Combina title e subtitle para formar a pergunta
            question = f"{title}"
            if subtitle:
                question += f" - {subtitle}"
            
            if not ticker or not question:
                return markets
            
            # Status do mercado
            status = market_data.get("status", "")
            if status not in ["open", "active"]:
                return markets
            
            # Precos (Kalshi usa formato _dollars ja em decimal ou centavos)
            # Tenta primeiro formato _dollars (string decimal)
            yes_bid_dollars = market_data.get("yes_bid_dollars")
            yes_ask_dollars = market_data.get("yes_ask_dollars")
            no_bid_dollars = market_data.get("no_bid_dollars")
            no_ask_dollars = market_data.get("no_ask_dollars")
            
            if yes_bid_dollars is not None:
                yes_bid = float(yes_bid_dollars)
                yes_ask = float(yes_ask_dollars) if yes_ask_dollars else 0
                no_bid = float(no_bid_dollars) if no_bid_dollars else 0
                no_ask = float(no_ask_dollars) if no_ask_dollars else 0
            else:
                # Formato antigo (centavos)
                yes_bid = float(market_data.get("yes_bid", 0) or 0) / 100.0
                yes_ask = float(market_data.get("yes_ask", 0) or 0) / 100.0
                no_bid = float(market_data.get("no_bid", 0) or 0) / 100.0
                no_ask = float(market_data.get("no_ask", 0) or 0) / 100.0
            
            # Volume e liquidez
            # Kalshi agora retorna liquidity_dollars e volume_24h
            liquidity_dollars = market_data.get("liquidity_dollars")
            volume_24h = float(market_data.get("volume_24h", 0) or 0)
            
            if liquidity_dollars:
                liquidity = float(liquidity_dollars)
            else:
                # Fallback: usa open_interest
                open_interest = float(market_data.get("open_interest", 0) or 0)
                liquidity = open_interest * 10
            
            # Data de fechamento
            close_time = market_data.get("close_time") or market_data.get("expiration_time") or market_data.get("expected_expiration_time")
            expires_at = None
            if close_time:
                try:
                    # Kalshi usa ISO 8601
                    expires_at = datetime.fromisoformat(close_time.replace('Z', '+00:00'))
                except:
                    pass
            
            # URL do mercado
            # Kalshi usa formato: /markets/EVENT_TICKER/MARKET_TICKER
            # Extrai o event ticker (parte antes do primeiro -)
            event_ticker = ticker.split('-')[0].lower() if '-' in ticker else ticker.lower()
            market_url = f"https://kalshi.com/markets/{event_ticker}/{ticker.lower()}"
            
            # Cria mercado YES (usa mid price entre bid e ask)
            yes_price = (yes_bid + yes_ask) / 2 if yes_ask > 0 else yes_bid
            # Kalshi: nao filtra aqui, deixa o filtro global fazer isso
            if yes_price > 0:
                market_yes = Market(
                    exchange=self.name,
                    market_id=f"{ticker}_YES",
                    question=question,
                    outcome="YES",
                    price=yes_price,
                    volume_24h=volume_24h,
                    liquidity=liquidity,
                    expires_at=expires_at,
                    url=market_url
                )
                markets.append(market_yes)
            
            # Cria mercado NO
            no_price = (no_bid + no_ask) / 2 if no_ask > 0 else no_bid
            # Kalshi: nao filtra aqui, deixa o filtro global fazer isso
            if no_price > 0:
                market_no = Market(
                    exchange=self.name,
                    market_id=f"{ticker}_NO",
                    question=question,
                    outcome="NO",
                    price=no_price,
                    volume_24h=volume_24h,
                    liquidity=liquidity,
                    expires_at=expires_at,
                    url=market_url
                )
                markets.append(market_no)
        
        except Exception as e:
            pass
        
        return markets
    
    async def get_market_orderbook(self, ticker: str) -> Optional[dict]:
        """
        Busca order book detalhado de um mercado especifico
        
        Endpoint: GET /markets/{ticker}/orderbook
        Docs: https://docs.kalshi.com/api-reference/orderbook
        
        Util para:
        - Ver liquidez real em cada nivel de preco
        - Calcular slippage esperado
        - Determinar tamanho maximo de trade
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.api_url}/markets/{ticker}/orderbook"
                response = await client.get(url, headers=self._get_headers())
                
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            print(f"Erro ao buscar orderbook: {e}")
        
        return None
