# -*- coding: utf-8 -*-
"""Matcher melhorado com identificacao de sinonimos e variantes"""
from typing import List, Tuple, Dict, Set
from exchanges.base import Market
from difflib import SequenceMatcher
import re


class ImprovedEventMatcher:
    """Matcher melhorado para encontrar eventos equivalentes com titulos diferentes"""
    
    def __init__(self, similarity_threshold: float = 0.45, max_date_diff_days: int = 7):
        self.similarity_threshold = similarity_threshold
        self.max_date_diff_days = max_date_diff_days  # Maximo de diferenca entre datas de expiracao
        
        # Cache de similaridade para evitar recalculos
        self._similarity_cache: Dict[Tuple[str, str], float] = {}
        self._entity_cache: Dict[str, Dict] = {}
        
        # Dicionario de sinonimos para eleicoes/politica
        self.synonyms = {
            # Eleicoes
            "nomination": ["primary", "primary winner", "nominee", "nominate"],
            "primary": ["nomination", "primary election", "primary winner"],
            "election": ["race", "contest"],
            "winner": ["who will win", "victor", "victorious", "prevail"],
            
            # Posicoes politicas
            "senate": ["senator", "senatorial"],
            "house": ["representative", "congressman", "congresswoman"],
            "governor": ["gubernatorial"],
            "president": ["presidential", "potus"],
            
            # Partidos
            "democratic": ["democrat", "dem", "d"],
            "republican": ["gop", "rep", "r"],
            
            # Acoes comuns
            "win": ["winner", "victory", "prevail", "triumph"],
            "lose": ["loser", "defeat", "beaten"],
            
            # Perguntas comuns
            "who will": ["which", "what", "winner"],
            "will": ["going to", "gonna"],
        }
        
        # Palavras que devem ser ignoradas (stop words especificas)
        self.stop_words = {
            "the", "a", "an", "will", "be", "is", "are", "in", "of", "to", "for",
            "on", "at", "by", "with", "from", "as", "into", "during", "including",
            "who", "what", "which", "when", "where", "how", "why"
        }
        
        # Padroes de data para normalizar
        self.date_patterns = [
            r'\b20\d{2}\b',  # Anos (2024, 2025, 2026...)
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b',
            r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b',
        ]
        
        # Dicionario de aliases de candidatos (nomes completos e apelidos)
        self.candidate_aliases = {
            # Presidentes e candidatos recentes
            "biden": ["joe biden", "joseph biden", "biden", "joe", "joseph r biden"],
            "trump": ["donald trump", "trump", "donald", "donald j trump"],
            "harris": ["kamala harris", "harris", "kamala"],
            "obama": ["barack obama", "obama", "barack"],
            "clinton": ["hillary clinton", "clinton", "hillary"],
            "sanders": ["bernie sanders", "sanders", "bernie", "bernard sanders"],
            "warren": ["elizabeth warren", "warren", "elizabeth"],
            "desantis": ["ron desantis", "desantis", "ron", "ronald desantis"],
            "pence": ["mike pence", "pence", "mike", "michael pence"],
            "newsom": ["gavin newsom", "newsom", "gavin"],
            "whitmer": ["gretchen whitmer", "whitmer", "gretchen"],
            "booker": ["cory booker", "booker", "cory"],
            "buttigieg": ["pete buttigieg", "buttigieg", "pete", "peter buttigieg"],
            "klobuchar": ["amy klobuchar", "klobuchar", "amy"],
            "cruz": ["ted cruz", "cruz", "ted", "rafael cruz"],
            "rubio": ["marco rubio", "rubio", "marco"],
            "haley": ["nikki haley", "haley", "nikki"],
            "scott": ["tim scott", "scott", "tim"],
            "ramaswamy": ["vivek ramaswamy", "ramaswamy", "vivek"],
            "vance": ["jd vance", "vance", "j d vance", "james vance"],
            "walz": ["tim walz", "walz", "tim"],
            "abbott": ["greg abbott", "abbott", "greg"],
            "youngkin": ["glenn youngkin", "youngkin", "glenn"],
        }
        
        # Dicionario de normalizacao de estados (abreviacoes -> nome completo)
        self.state_normalizations = {
            # Abreviacoes oficiais
            "al": "alabama", "ak": "alaska", "az": "arizona", "ar": "arkansas",
            "ca": "california", "co": "colorado", "ct": "connecticut", "de": "delaware",
            "fl": "florida", "ga": "georgia", "hi": "hawaii", "id": "idaho",
            "il": "illinois", "in": "indiana", "ia": "iowa", "ks": "kansas",
            "ky": "kentucky", "la": "louisiana", "me": "maine", "md": "maryland",
            "ma": "massachusetts", "mi": "michigan", "mn": "minnesota", "ms": "mississippi",
            "mo": "missouri", "mt": "montana", "ne": "nebraska", "nv": "nevada",
            "nh": "new hampshire", "nj": "new jersey", "nm": "new mexico", "ny": "new york",
            "nc": "north carolina", "nd": "north dakota", "oh": "ohio", "ok": "oklahoma",
            "or": "oregon", "pa": "pennsylvania", "ri": "rhode island", "sc": "south carolina",
            "sd": "south dakota", "tn": "tennessee", "tx": "texas", "ut": "utah",
            "vt": "vermont", "va": "virginia", "wa": "washington", "wv": "west virginia",
            "wi": "wisconsin", "wy": "wyoming", "dc": "district of columbia",
            # Aliases comuns
            "calif": "california", "mass": "massachusetts", "penn": "pennsylvania",
            "n.y.": "new york", "n.j.": "new jersey", "n.c.": "north carolina",
            "s.c.": "south carolina", "n.d.": "north dakota", "s.d.": "south dakota",
            "w.va": "west virginia", "wash": "washington",
        }
        
        # Dicionario de paises e seus sinonimos/variacoes
        self.countries = {
            "united_states": ["united states", "usa", "us", "america", "american", "u.s.", "u.s.a."],
            "united_kingdom": ["united kingdom", "uk", "britain", "british", "great britain", "u.k."],
            "canada": ["canada", "canadian"],
            "australia": ["australia", "australian", "aussie"],
            "brazil": ["brazil", "brazilian", "brasil"],
            "mexico": ["mexico", "mexican"],
            "argentina": ["argentina", "argentinian"],
            "france": ["france", "french"],
            "germany": ["germany", "german", "deutschland"],
            "italy": ["italy", "italian"],
            "spain": ["spain", "spanish"],
            "portugal": ["portugal", "portuguese"],
            "russia": ["russia", "russian"],
            "china": ["china", "chinese"],
            "japan": ["japan", "japanese"],
            "south_korea": ["south korea", "korea", "korean", "s. korea"],
            "india": ["india", "indian"],
            "turkey": ["turkey", "turkish"],
            "israel": ["israel", "israeli"],
            "saudi_arabia": ["saudi arabia", "saudi", "ksa"],
            "uae": ["uae", "united arab emirates", "dubai", "emirates"],
            "south_africa": ["south africa", "south african"],
            "nigeria": ["nigeria", "nigerian"],
            "egypt": ["egypt", "egyptian"],
        }
    
    def expand_with_synonyms(self, word: str) -> Set[str]:
        """Expande uma palavra com seus sinonimos"""
        word_lower = word.lower()
        expanded = {word_lower}
        
        # Adiciona sinonimos diretos
        if word_lower in self.synonyms:
            expanded.update(self.synonyms[word_lower])
        
        # Verifica se a palavra eh sinonimo de alguma chave
        for key, syns in self.synonyms.items():
            if word_lower in syns:
                expanded.add(key)
                expanded.update(syns)
        
        return expanded
    
    def extract_key_terms(self, question: str) -> Set[str]:
        """Extrai termos-chave de uma questao, expandindo com sinonimos"""
        # Normaliza
        question = question.lower()
        question = re.sub(r'[^\w\s]', ' ', question)
        
        # Remove stop words
        words = [w for w in question.split() if w not in self.stop_words and len(w) > 2]
        
        # Expande com sinonimos
        key_terms = set()
        for word in words:
            key_terms.update(self.expand_with_synonyms(word))
        
        return key_terms
    
    def extract_entities(self, question: str) -> Dict[str, List[str]]:
        """Extrai entidades especificas (locais, anos, nomes, paises, candidatos)"""
        entities = {
            "years": [],
            "states": [],
            "parties": [],
            "positions": [],
            "countries": [],
            "candidates": [],  # NOVO!
            "question_type": None  # NOVO! "who_will_win" vs "will_x_win"
        }
        
        question_lower = question.lower()
        
        # Anos
        years = re.findall(r'\b(20\d{2})\b', question)
        entities["years"] = years
        
        # PAISES (CRITICO para evitar falsos positivos!)
        for country_key, country_variants in self.countries.items():
            for variant in country_variants:
                # Usa word boundary para evitar matches parciais
                pattern = r'\b' + re.escape(variant) + r'\b'
                if re.search(pattern, question_lower):
                    entities["countries"].append(country_key)
                    break  # Ja encontrou este pais
        
        # Estados americanos - detecta e normaliza
        # Primeiro, normaliza abreviacoes
        words_in_question = question_lower.split()
        normalized_states = set()
        
        for word in words_in_question:
            # Remove pontuacao para pegar "TX," ou "NY."
            clean_word = re.sub(r'[^\w]', '', word).lower()
            if clean_word in self.state_normalizations:
                normalized_states.add(self.state_normalizations[clean_word])
        
        # Depois, busca nomes completos no texto
        all_states = set(self.state_normalizations.values())
        for state in all_states:
            if state in question_lower:
                normalized_states.add(state)
        
        # Adiciona todos os estados normalizados
        entities["states"].extend(list(normalized_states))
        
        # Se menciona estado americano, provavelmente eh sobre US
        if normalized_states and "united_states" not in entities["countries"]:
            entities["countries"].append("united_states")
        
        # Partidos
        if any(word in question_lower for word in ["democratic", "democrat", "dem"]):
            entities["parties"].append("democratic")
        if any(word in question_lower for word in ["republican", "gop", "rep"]):
            entities["parties"].append("republican")
        
        # Posicoes
        positions = ["senate", "senator", "house", "representative", "governor", 
                    "president", "presidential", "congressional", "prime minister",
                    "chancellor", "mayor"]
        for pos in positions:
            if pos in question_lower:
                entities["positions"].append(pos)
        
        # CANDIDATOS - Nomes proprios (palavras capitalizadas)
        # Extrai palavras que parecem ser nomes de pessoas
        words = question.split()
        
        # Lista de stop words a ignorar
        stop_words = {
            "who", "will", "the", "what", "when", "where", "how", "why", 
            "which", "would", "should", "could", "may", "might", "can",
            "democratic", "republican", "senate", "house", "president", "presidential",
            "governor", "gubernatorial", "election", "primary", "nomination",
            "winner", "candidate", "race", "contest", "party", "win", "wins"
        }
        
        raw_candidates = []
        for i, word in enumerate(words):
            # Nome proprio: comeca com maiuscula, tem mais de 2 letras
            if word and len(word) > 2 and word[0].isupper():
                # Remove pontuacao
                clean_word = re.sub(r'[^\w]', '', word)
                if clean_word and len(clean_word) > 2:
                    # Nao eh stop word
                    if clean_word.lower() not in stop_words:
                        # Verifica se nao eh nome de estado
                        all_state_names = set(self.state_normalizations.values())
                        if clean_word.lower() not in all_state_names:
                            raw_candidates.append(clean_word)
        
        # Normaliza candidatos usando aliases
        normalized_candidates = set()
        question_lower_full = question.lower()
        
        # Primeiro, tenta encontrar candidatos conhecidos por alias
        for canonical_name, aliases in self.candidate_aliases.items():
            for alias in aliases:
                # Usa word boundary para evitar matches parciais
                pattern = r'\b' + re.escape(alias) + r'\b'
                if re.search(pattern, question_lower_full):
                    normalized_candidates.add(canonical_name)
                    break
        
        # Se nao encontrou nenhum candidato conhecido, usa os raw
        if not normalized_candidates:
            entities["candidates"] = raw_candidates
        else:
            entities["candidates"] = list(normalized_candidates)
        
        # TIPO DE QUESTAO (antes de determinar candidatos)
        question_lower_clean = question_lower.strip()
        
        # "Will X win" - pergunta binaria sobre pessoa especifica (PRIORIDADE!)
        if question_lower_clean.startswith("will ") and " win" in question_lower:
            # Verifica se ha nome proprio depois de "Will"
            words_after_will = question_lower_clean.split("will ", 1)
            if len(words_after_will) > 1:
                first_word = words_after_will[1].split()[0] if words_after_will[1].split() else ""
                # Se a primeira palavra apos "will" eh nome proprio
                matching_word = next((w for w in words if w.lower() == first_word), None)
                if matching_word and matching_word[0].isupper():
                    entities["question_type"] = "will_x_win"
        
        # "Who will win" - pergunta aberta
        if not entities["question_type"]:
            if question_lower_clean.startswith("who will") or "who will win" in question_lower:
                entities["question_type"] = "who_will_win"
        
        # "X to win" ou "X winner"
        if not entities["question_type"]:
            if " to win" in question_lower or "winner" in question_lower:
                entities["question_type"] = "x_winner"
        
        return entities
    
    def calculate_enhanced_similarity(self, q1: str, q2: str) -> float:
        """Calcula similaridade melhorada usando sinonimos e entidades (COM CACHE)"""
        
        # Cache: verifica se já calculamos esta combinação
        cache_key = (q1, q2) if q1 < q2 else (q2, q1)
        if cache_key in self._similarity_cache:
            return self._similarity_cache[cache_key]
        
        # 1. Similaridade basica de sequencia
        base_similarity = SequenceMatcher(None, q1.lower(), q2.lower()).ratio()
        
        # 2. Similaridade de termos-chave (com sinonimos)
        terms1 = self.extract_key_terms(q1)
        terms2 = self.extract_key_terms(q2)
        
        if not terms1 or not terms2:
            term_similarity = 0
        else:
            intersection = len(terms1 & terms2)
            union = len(terms1 | terms2)
            term_similarity = intersection / union if union > 0 else 0
        
        # 3. Similaridade de entidades (MUITO IMPORTANTE!)
        # Usa cache para extração de entidades
        if q1 not in self._entity_cache:
            self._entity_cache[q1] = self.extract_entities(q1)
        if q2 not in self._entity_cache:
            self._entity_cache[q2] = self.extract_entities(q2)
        
        entities1 = self._entity_cache[q1]
        entities2 = self._entity_cache[q2]
        
        entity_matches = 0
        entity_total = 0
        
        for key in entities1.keys():
            if entities1[key] and entities2[key]:
                entity_total += 1
                # Se pelo menos uma entidade coincide, conta como match
                if any(e in entities2[key] for e in entities1[key]):
                    entity_matches += 1
        
        entity_similarity = entity_matches / entity_total if entity_total > 0 else 0
        
        # 4. Score final ponderado
        # Entidades sao MUITO importantes (50%)
        # Termos-chave com sinonimos (35%)
        # Similaridade basica (15%)
        final_score = (
            entity_similarity * 0.50 +
            term_similarity * 0.35 +
            base_similarity * 0.15
        )
        
        # Armazena no cache
        self._similarity_cache[cache_key] = final_score
        
        return final_score
    
    def are_markets_equivalent(self, market1: Market, market2: Market) -> Tuple[bool, float, Dict]:
        """Verifica se dois mercados sao equivalentes com analise detalhada"""
        
        # Nao compara mercados da mesma exchange
        if market1.exchange == market2.exchange:
            return False, 0.0, {"reason": "same_exchange"}
        
        # VALIDACAO #0: DATA DE EXPIRACAO (se ambos tiverem)
        if market1.expires_at and market2.expires_at:
            # Torna ambos timezone-aware se necessario
            from datetime import timezone
            exp1 = market1.expires_at if market1.expires_at.tzinfo else market1.expires_at.replace(tzinfo=timezone.utc)
            exp2 = market2.expires_at if market2.expires_at.tzinfo else market2.expires_at.replace(tzinfo=timezone.utc)
            
            date_diff = abs((exp1 - exp2).days)
            
            # Se diferenca maior que limite, rejeita
            if date_diff > self.max_date_diff_days:
                return False, 0.0, {
                    "reason": "different_expiration_dates",
                    "date_diff_days": date_diff,
                    "max_allowed": self.max_date_diff_days
                }
        
        # Extrai entidades para comparacao
        entities1 = self.extract_entities(market1.question)
        entities2 = self.extract_entities(market2.question)
        
        # REGRA CRITICA #1: PAIS deve ser o mesmo (MAIS IMPORTANTE!)
        # Se ambos mencionam pais, DEVEM ser o mesmo
        if entities1["countries"] and entities2["countries"]:
            if not any(c in entities2["countries"] for c in entities1["countries"]):
                return False, 0.0, {
                    "reason": "different_countries",
                    "country1": entities1["countries"],
                    "country2": entities2["countries"]
                }
        
        # REGRA CRITICA #2: Ano deve ser o mesmo
        if entities1["years"] and entities2["years"]:
            if not any(y in entities2["years"] for y in entities1["years"]):
                return False, 0.0, {"reason": "different_years"}
        
        # REGRA CRITICA #3: Estado deve ser o mesmo (se ambos mencionam estado)
        if entities1["states"] and entities2["states"]:
            if not any(s in entities2["states"] for s in entities1["states"]):
                return False, 0.0, {"reason": "different_states"}
        
        # REGRA CRITICA #4: Partido deve ser o mesmo (se ambos mencionam partido)
        if entities1["parties"] and entities2["parties"]:
            if not any(p in entities2["parties"] for p in entities1["parties"]):
                return False, 0.0, {"reason": "different_parties"}
        
        # REGRA CRITICA #5: Posicao deve ser compativel
        if entities1["positions"] and entities2["positions"]:
            if not any(p in entities2["positions"] for p in entities1["positions"]):
                return False, 0.0, {"reason": "different_positions"}
        
        # REGRA CRITICA #6: TIPO DE QUESTAO deve ser compativel
        # "Who will win?" vs "Will Biden win?" sao diferentes
        type1 = entities1.get("question_type")
        type2 = entities2.get("question_type")
        
        # Extrai candidatos para analisar antes de rejeitar por tipo
        candidates1 = set(c.lower() for c in entities1["candidates"])
        candidates2 = set(c.lower() for c in entities2["candidates"])
        
        if type1 and type2:
            # "will_x_win" e "x_winner" podem matchear SE o candidato for o mesmo
            compatible_types = {
                ("will_x_win", "will_x_win"),
                ("will_x_win", "x_winner"),
                ("x_winner", "will_x_win"),
                ("x_winner", "x_winner"),
                ("who_will_win", "who_will_win"),
                ("who_will_win", "x_winner"),
                ("x_winner", "who_will_win"),
            }
            
            type_pair = (type1, type2)
            
            # Se eh pergunta aberta vs binaria especifica, REJEITA
            if type1 == "who_will_win" and type2 == "will_x_win":
                return False, 0.0, {
                    "reason": "different_question_types",
                    "type1": type1,
                    "type2": type2
                }
            if type2 == "who_will_win" and type1 == "will_x_win":
                return False, 0.0, {
                    "reason": "different_question_types",
                    "type1": type1,
                    "type2": type2
                }
        
        # REGRA CRITICA #7: CANDIDATOS especificos devem ser os mesmos
        # Ja extraimos os candidatos acima (candidates1, candidates2)
        # Candidatos ja vem normalizados (aliases resolvidos)
        
        if candidates1 and candidates2:
            # Se ambos mencionam candidatos mas nenhum em comum, rejeita
            common_candidates = candidates1 & candidates2
            if not common_candidates:
                # Permite se um dos mercados tem MUITOS candidatos (lista geral)
                # vs outro tem poucos (especifico)
                if len(candidates1) < 5 and len(candidates2) < 5:
                    return False, 0.0, {
                        "reason": "different_candidates",
                        "candidates1": list(candidates1),
                        "candidates2": list(candidates2),
                        "note": "Candidatos ja normalizados via aliases"
                    }
        
        # Calcula similaridade melhorada
        similarity = self.calculate_enhanced_similarity(market1.question, market2.question)
        
        details = {
            "similarity": similarity,
            "entities1": entities1,
            "entities2": entities2,
            "q1": market1.question,
            "q2": market2.question,
            "exchange1": market1.exchange,
            "exchange2": market2.exchange
        }
        
        # Aumenta threshold para evitar falsos positivos
        is_match = similarity >= self.similarity_threshold
        
        return is_match, similarity, details
    
    def _quick_filter(self, q1: str, q2: str) -> bool:
        """Filtro rápido para descartar pares obviamente diferentes"""
        q1_lower = q1.lower()
        q2_lower = q2.lower()
        
        # Extrai palavras importantes (mais de 3 letras)
        words1 = set(w for w in q1_lower.split() if len(w) > 3)
        words2 = set(w for w in q2_lower.split() if len(w) > 3)
        
        # Se não tem pelo menos 2 palavras em comum, descarta
        common = words1 & words2
        if len(common) < 2:
            return False
        
        return True
    
    def find_matching_events(self, markets: List[Market]) -> List[Tuple[Market, Market]]:
        """Encontra pares de eventos equivalentes (ULTRA OTIMIZADO)"""
        matches = []
        checked = set()
        
        # Agrupa mercados por exchange
        by_exchange = {}
        for m in markets:
            ex = m.exchange.lower()
            if ex not in by_exchange:
                by_exchange[ex] = []
            by_exchange[ex].append(m)
        
        exchanges = list(by_exchange.keys())
        total_comparisons = 0
        quick_filtered = 0
        
        print(f"[Matcher] {len(markets)} mercados em {len(exchanges)} exchanges")
        
        # Só compara mercados de exchanges DIFERENTES
        for i, ex1 in enumerate(exchanges):
            for ex2 in exchanges[i+1:]:
                markets1 = by_exchange[ex1]
                markets2 = by_exchange[ex2]
                
                for market1 in markets1:
                    for market2 in markets2:
                        total_comparisons += 1
                        
                        # Filtro ultra-rápido primeiro
                        if not self._quick_filter(market1.question, market2.question):
                            quick_filtered += 1
                            continue
                        
                        pair_key = tuple(sorted([f"{market1.exchange}:{market1.market_id}", 
                                                f"{market2.exchange}:{market2.market_id}"]))
                        
                        if pair_key in checked:
                            continue
                        checked.add(pair_key)
                        
                        is_match, similarity, details = self.are_markets_equivalent(market1, market2)
                        
                        if is_match:
                            matches.append((market1, market2))
        
        print(f"[Matcher] {total_comparisons} total, {quick_filtered} filtrados, {len(matches)} matches")
        return matches


# Funcao para testar com o exemplo do usuario
def test_texas_senate_example():
    """Testa o matcher com o exemplo do Texas Senate"""
    from exchanges.base import Market
    from datetime import datetime
    
    # Simula os dois mercados
    predictit_market = Market(
        exchange="predictit",
        market_id="8180",
        question="Who will win the 2026 Texas Democratic Senate nomination",
        outcome="Yes",
        price=0.50,
        volume_24h=5000,
        liquidity=10000,
        expires_at=datetime(2026, 3, 3),
        url="https://www.predictit.org/markets/detail/8180/"
    )
    
    polymarket_market = Market(
        exchange="polymarket",
        market_id="texas-dem-senate",
        question="Texas Democratic Senate Primary Winner",
        outcome="Yes",
        price=0.49,
        volume_24h=9302,
        liquidity=15000,
        expires_at=datetime(2026, 3, 3),
        url="https://polymarket.com/event/texas-democratic-senate-primary-winner"
    )
    
    matcher = ImprovedEventMatcher(similarity_threshold=0.45)
    
    is_match, similarity, details = matcher.are_markets_equivalent(
        predictit_market, 
        polymarket_market
    )
    
    print("\n" + "="*60)
    print("TESTE: Texas Democratic Senate 2026")
    print("="*60)
    print(f"\nPredictIt: {predictit_market.question}")
    print(f"Polymarket: {polymarket_market.question}")
    print(f"\nMatch: {is_match}")
    print(f"Similaridade: {similarity:.2%}")
    print(f"\nEntidades PredictIt: {details['entities1']}")
    print(f"Entidades Polymarket: {details['entities2']}")
    print(f"\nTermos-chave extraidos:")
    print(f"  PredictIt: {matcher.extract_key_terms(predictit_market.question)}")
    print(f"  Polymarket: {matcher.extract_key_terms(polymarket_market.question)}")
    
    if is_match:
        # Calcula oportunidade de arbitragem
        price_diff = abs(predictit_market.price - polymarket_market.price)
        potential_profit = (price_diff / min(predictit_market.price, polymarket_market.price)) * 100
        
        print(f"\n" + "="*60)
        print("OPORTUNIDADE DE ARBITRAGEM DETECTADA!")
        print("="*60)
        print(f"PredictIt preco: ${predictit_market.price:.3f}")
        print(f"Polymarket preco: ${polymarket_market.price:.3f}")
        print(f"Diferenca: ${price_diff:.3f}")
        print(f"Lucro potencial: {potential_profit:.2f}%")
        
        if predictit_market.price < polymarket_market.price:
            print(f"\nESTRATEGIA:")
            print(f"  1. COMPRAR em PredictIt @ ${predictit_market.price:.3f}")
            print(f"  2. VENDER em Polymarket @ ${polymarket_market.price:.3f}")
        else:
            print(f"\nESTRATEGIA:")
            print(f"  1. COMPRAR em Polymarket @ ${polymarket_market.price:.3f}")
            print(f"  2. VENDER em PredictIt @ ${predictit_market.price:.3f}")


if __name__ == "__main__":
    test_texas_senate_example()

