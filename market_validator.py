"""Validador de equivalência de mercados para evitar falsas arbitragens"""
from typing import List, Tuple, Dict
from exchanges.base import Market
from datetime import datetime, timedelta
import re


class MarketValidator:
    """Valida se dois mercados representam o mesmo evento"""
    
    def __init__(self):
        self.date_tolerance_days = 1  # Tolerância de 1 dia para datas de resolução
    
    def validate_equivalence(
        self, 
        market1: Market, 
        market2: Market,
        min_similarity: float = 0.70
    ) -> Tuple[bool, Dict]:
        """Valida se dois mercados são equivalentes"""
        
        validation_result = {
            "equivalent": False,
            "confidence": 0.0,
            "issues": [],
            "checks": {}
        }
        
        # Check 1: Similaridade de texto
        from matcher import EventMatcher
        matcher = EventMatcher()
        similarity = matcher.calculate_similarity(market1.question, market2.question)
        validation_result["checks"]["text_similarity"] = similarity
        
        if similarity < min_similarity:
            validation_result["issues"].append(f"Similaridade de texto baixa: {similarity:.2%}")
            return False, validation_result
        
        # Check 2: Mesmo outcome
        if market1.outcome != market2.outcome:
            validation_result["issues"].append(f"Outcomes diferentes: {market1.outcome} vs {market2.outcome}")
            return False, validation_result
        validation_result["checks"]["same_outcome"] = True
        
        # Check 3: Datas de expiração similares (se disponíveis)
        if market1.expires_at and market2.expires_at:
            date_diff = abs((market1.expires_at - market2.expires_at).days)
            validation_result["checks"]["date_difference_days"] = date_diff
            
            if date_diff > self.date_tolerance_days:
                validation_result["issues"].append(
                    f"Datas de expiração muito diferentes: {date_diff} dias"
                )
                # Não é crítico, mas reduz confiança
                validation_result["confidence"] = similarity * 0.8
            else:
                validation_result["confidence"] = similarity
        else:
            validation_result["confidence"] = similarity * 0.9  # Reduz confiança se não tem data
        
        # Check 4: Preços válidos
        if market1.price <= 0 or market1.price > 1 or market2.price <= 0 or market2.price > 1:
            validation_result["issues"].append("Preços inválidos")
            return False, validation_result
        
        # Check 4b: Evita mercados resolvidos (preço = 1.0 ou 0.0)
        if market1.price >= 0.99 or market1.price <= 0.01 or market2.price >= 0.99 or market2.price <= 0.01:
            validation_result["issues"].append("Mercado já resolvido ou certeza absoluta")
            return False, validation_result
        
        validation_result["checks"]["valid_prices"] = True
        
        # Check 5: Liquidez suficiente
        min_liquidity = min(market1.liquidity, market2.liquidity)
        validation_result["checks"]["min_liquidity"] = min_liquidity
        
        if min_liquidity < 100:
            validation_result["issues"].append(f"Liquidez insuficiente: ${min_liquidity:.2f}")
            # Não é crítico, mas reduz confiança
            validation_result["confidence"] *= 0.9
        
        # Se passou todos os checks críticos
        if not validation_result["issues"] or all(
            "Liquidez" in issue or "Datas" in issue 
            for issue in validation_result["issues"]
        ):
            validation_result["equivalent"] = True
        
        return validation_result["equivalent"], validation_result
    
    def extract_keywords(self, question: str) -> List[str]:
        """Extrai palavras-chave importantes de uma pergunta"""
        # Remove stop words e pega palavras significativas
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'will', 'be', 'is', 'are', 'was', 'were'}
        
        # Normaliza
        text = re.sub(r'[^\w\s]', '', question.lower())
        words = text.split()
        
        # Filtra palavras significativas (mais de 3 caracteres, não stop words)
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        
        return keywords[:10]  # Top 10 keywords
    
    def validate_market_pair(self, market1: Market, market2: Market) -> Dict:
        """Validação completa de um par de mercados"""
        equivalent, details = self.validate_equivalence(market1, market2)
        
        # Adiciona informações extras
        details["market1"] = {
            "exchange": market1.exchange,
            "question": market1.question[:50],
            "price": market1.price,
            "liquidity": market1.liquidity
        }
        details["market2"] = {
            "exchange": market2.exchange,
            "question": market2.question[:50],
            "price": market2.price,
            "liquidity": market2.liquidity
        }
        
        details["keywords1"] = self.extract_keywords(market1.question)
        details["keywords2"] = self.extract_keywords(market2.question)
        details["common_keywords"] = list(set(details["keywords1"]) & set(details["keywords2"]))
        
        return details

