"""
Camada de Matching e Normalização de Mercados

Garante que estamos comparando eventos equivalentes entre plataformas:
- Mesmo outcome (YES vs YES, NO vs NO)
- Mesma data de resolução
- Mesmo evento/mercado
"""
from typing import List, Tuple, Optional
from exchanges.base import Market
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import re


class MarketNormalizer:
    """
    Normaliza e valida equivalência entre mercados de diferentes exchanges
    """
    
    def __init__(
        self,
        min_text_similarity: float = 0.60,
        max_date_difference_days: int = 1,
        require_same_outcome: bool = True
    ):
        """
        Args:
            min_text_similarity: Similaridade mínima de texto (0-1)
            max_date_difference_days: Diferença máxima em dias para datas de resolução
            require_same_outcome: Exige mesmo outcome (YES/NO)
        """
        self.min_text_similarity = min_text_similarity
        self.max_date_difference_days = max_date_difference_days
        self.require_same_outcome = require_same_outcome
    
    def normalize_text(self, text: str) -> str:
        """Normaliza texto para comparação"""
        # Remove pontuação e lowercase
        text = re.sub(r'[^\w\s]', '', text.lower())
        
        # Remove espaços múltiplos
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove stop words comuns
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'will', 'be', 'have', 'has', 'is', 'are', 'was',
            'were', 'been', 'being', 'do', 'does', 'did', 'done', 'doing'
        }
        
        words = [w for w in text.split() if w not in stop_words]
        return ' '.join(words)
    
    def extract_keywords(self, text: str) -> set:
        """Extrai palavras-chave importantes"""
        normalized = self.normalize_text(text)
        
        # Palavras com mais de 3 caracteres
        keywords = {w for w in normalized.split() if len(w) > 3}
        
        return keywords
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calcula similaridade entre dois textos
        
        Returns:
            float: Similaridade de 0 a 1
        """
        norm1 = self.normalize_text(text1)
        norm2 = self.normalize_text(text2)
        
        # Similaridade de sequência
        seq_similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        # Similaridade de palavras-chave
        keywords1 = self.extract_keywords(text1)
        keywords2 = self.extract_keywords(text2)
        
        if not keywords1 or not keywords2:
            return seq_similarity
        
        common = keywords1.intersection(keywords2)
        total = keywords1.union(keywords2)
        
        keyword_similarity = len(common) / len(total) if total else 0
        
        # Média ponderada (70% keywords, 30% sequência)
        similarity = (keyword_similarity * 0.7) + (seq_similarity * 0.3)
        
        # Bonus se compartilham muitas keywords importantes
        if len(common) >= 3:
            similarity *= 1.15
        
        return min(similarity, 1.0)
    
    def check_date_equivalence(
        self,
        date1: Optional[datetime],
        date2: Optional[datetime]
    ) -> Tuple[bool, Optional[int]]:
        """
        Verifica se duas datas são equivalentes
        
        Returns:
            Tuple[bool, Optional[int]]: (são_equivalentes, diferença_em_dias)
        """
        if not date1 or not date2:
            # Se uma ou ambas não têm data, considera equivalente
            return True, None
        
        try:
            diff = abs((date1 - date2).days)
            is_equivalent = diff <= self.max_date_difference_days
            return is_equivalent, diff
        except:
            return True, None
    
    def are_markets_equivalent(
        self,
        market1: Market,
        market2: Market
    ) -> Tuple[bool, dict]:
        """
        Verifica se dois mercados representam o mesmo evento
        
        Returns:
            Tuple[bool, dict]: (são_equivalentes, detalhes_da_validação)
        """
        validation = {
            "equivalent": False,
            "text_similarity": 0.0,
            "same_outcome": False,
            "date_difference_days": None,
            "issues": [],
            "confidence": 0.0
        }
        
        # 1. Verifica se são da mesma exchange (não faz sentido comparar)
        if market1.exchange == market2.exchange:
            validation["issues"].append("Mesma exchange")
            return False, validation
        
        # 2. Similaridade de texto
        text_sim = self.calculate_text_similarity(market1.question, market2.question)
        validation["text_similarity"] = text_sim
        
        if text_sim < self.min_text_similarity:
            validation["issues"].append(f"Similaridade de texto baixa: {text_sim:.2%}")
            return False, validation
        
        # 3. Mesmo outcome
        same_outcome = market1.outcome == market2.outcome
        validation["same_outcome"] = same_outcome
        
        if self.require_same_outcome and not same_outcome:
            validation["issues"].append(f"Outcomes diferentes: {market1.outcome} vs {market2.outcome}")
            return False, validation
        
        # 4. Datas equivalentes
        dates_ok, date_diff = self.check_date_equivalence(
            market1.expires_at,
            market2.expires_at
        )
        validation["date_difference_days"] = date_diff
        
        if not dates_ok:
            validation["issues"].append(f"Datas muito diferentes: {date_diff} dias")
            # Não é crítico, mas reduz confiança
            validation["confidence"] = text_sim * 0.7
        else:
            validation["confidence"] = text_sim
        
        # 5. Preços válidos
        if market1.price <= 0 or market1.price >= 1 or market2.price <= 0 or market2.price >= 1:
            validation["issues"].append("Preços inválidos")
            return False, validation
        
        # 6. Mercados já resolvidos (certeza absoluta)
        if market1.price >= 0.99 or market1.price <= 0.01:
            validation["issues"].append(f"Mercado 1 já resolvido: ${market1.price:.3f}")
            return False, validation
        
        if market2.price >= 0.99 or market2.price <= 0.01:
            validation["issues"].append(f"Mercado 2 já resolvido: ${market2.price:.3f}")
            return False, validation
        
        # Se passou todos os checks críticos
        if not validation["issues"] or (
            validation["issues"] and 
            all("Datas" in issue for issue in validation["issues"])
        ):
            validation["equivalent"] = True
        
        return validation["equivalent"], validation
    
    def find_equivalent_pairs(
        self,
        markets: List[Market]
    ) -> List[Tuple[Market, Market, dict]]:
        """
        Encontra todos os pares equivalentes em uma lista de mercados
        
        Returns:
            List[Tuple[Market, Market, dict]]: Lista de (mercado1, mercado2, validação)
        """
        equivalent_pairs = []
        
        # Agrupa por exchange
        by_exchange = {}
        for market in markets:
            if market.exchange not in by_exchange:
                by_exchange[market.exchange] = []
            by_exchange[market.exchange].append(market)
        
        exchanges = list(by_exchange.keys())
        
        # Compara mercados de exchanges diferentes
        for i in range(len(exchanges)):
            for j in range(i + 1, len(exchanges)):
                ex1 = exchanges[i]
                ex2 = exchanges[j]
                
                for m1 in by_exchange[ex1]:
                    for m2 in by_exchange[ex2]:
                        is_equivalent, validation = self.are_markets_equivalent(m1, m2)
                        
                        if is_equivalent:
                            equivalent_pairs.append((m1, m2, validation))
        
        return equivalent_pairs

