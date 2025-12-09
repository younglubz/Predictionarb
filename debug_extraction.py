# -*- coding: utf-8 -*-
"""Debug da extracao de entidades"""
from matcher_improved import ImprovedEventMatcher

matcher = ImprovedEventMatcher()

questions = [
    "Will Kamala Harris win the 2028 Democratic nomination?",
    "Kamala Harris to win 2028 Democratic primary",
    "Will Gavin Newsom win the 2028 Democratic nomination?",
    "Who will win the 2028 presidential election?",
    "Will Biden win the 2028 presidential election?",
]

print("\n=== DEBUG: EXTRACAO DE ENTIDADES ===\n")

for q in questions:
    entities = matcher.extract_entities(q)
    print(f"Questao: {q}")
    print(f"  Candidatos: {entities.get('candidates', [])}")
    print(f"  Tipo: {entities.get('question_type', 'None')}")
    print()

