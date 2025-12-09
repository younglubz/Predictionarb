"""Integração com Augur"""
import httpx
from typing import List
from exchanges.base import ExchangeBase, Market
from datetime import datetime
import re


class AugurExchange(ExchangeBase):
    """Cliente para Augur API"""
    
    def __init__(self):
        super().__init__("augur")
        # Augur v2 não está mais ativo publicamente
        # A API pública foi descontinuada
        self.base_url = "https://api.augur.net"
    
    def normalize_question(self, question: str) -> str:
        """Normaliza pergunta"""
        normalized = re.sub(r'[^\w\s]', '', question.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    async def fetch_markets(self) -> List[Market]:
        """Busca mercados ativos do Augur"""
        # Augur não está mais disponível publicamente
        # A API pública foi descontinuada
        # Retorna lista vazia até encontrar alternativa
        return []
