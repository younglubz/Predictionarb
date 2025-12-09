"""Sistema de matching de eventos entre exchanges"""
from typing import List, Dict, Tuple
from exchanges.base import Market
from difflib import SequenceMatcher
import re


class EventMatcher:
    """Identifica eventos similares entre diferentes exchanges"""
    
    def __init__(self, similarity_threshold: float = 0.45):
        # Threshold de 0.45 (45%) RELAXADO para encontrar mais oportunidades
        # ATENCAO: Aumenta falsos positivos - validacao manual necessaria
        self.similarity_threshold = similarity_threshold
    
    def normalize_text(self, text: str) -> str:
        """Normaliza texto para comparação"""
        # Remove caracteres especiais
        text = re.sub(r'[^\w\s]', '', text.lower())
        # Remove espaços múltiplos
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove palavras comuns (mais agressivo)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                     'will', 'be', 'have', 'has', 'is', 'are', 'was', 'were', 'been', 'being',
                     'do', 'does', 'did', 'done', 'doing', 'would', 'could', 'should'}
        words = [w for w in text.split() if w not in stop_words]
        return ' '.join(words)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridade entre dois textos"""
        norm1 = self.normalize_text(text1)
        norm2 = self.normalize_text(text2)
        
        # Usa SequenceMatcher para similaridade
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        # Bonus para palavras-chave em comum (mais peso)
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        common_words = words1.intersection(words2)
        if len(words1) > 0 and len(words2) > 0:
            word_overlap = len(common_words) / max(len(words1), len(words2))
            # Dá mais peso ao word_overlap (70%) do que à sequência (30%)
            similarity = (similarity * 0.3) + (word_overlap * 0.7)
        
        # Bonus extra se compartilham palavras-chave importantes
        important_words = common_words - {'yes', 'no', '2024', '2025', 'market', 'prediction'}
        if len(important_words) >= 3:
            similarity *= 1.2  # Boost de 20%
        
        return min(similarity, 1.0)  # Cap em 1.0
    
    def find_matching_events(self, markets: List[Market]) -> List[Tuple[Market, Market]]:
        """Encontra pares de mercados que representam o mesmo evento"""
        matches = []
        
        # Agrupa por exchange
        by_exchange: Dict[str, List[Market]] = {}
        for market in markets:
            if market.exchange not in by_exchange:
                by_exchange[market.exchange] = []
            by_exchange[market.exchange].append(market)
        
        exchanges = list(by_exchange.keys())
        
        # Compara mercados de exchanges diferentes
        for i in range(len(exchanges)):
            for j in range(i + 1, len(exchanges)):
                exchange1 = exchanges[i]
                exchange2 = exchanges[j]
                
                for market1 in by_exchange[exchange1]:
                    for market2 in by_exchange[exchange2]:
                        similarity = self.calculate_similarity(
                            market1.question,
                            market2.question
                        )
                        
                        # Verifica se são o mesmo tipo de outcome
                        if (similarity >= self.similarity_threshold and
                            market1.outcome == market2.outcome):
                            matches.append((market1, market2))
        
        return matches

