# Configuracao de Filtros - Sistema de Arbitragem

## Filtros Atualizados (MENOS RIGOROSOS)

Os filtros foram ajustados para encontrar MAIS oportunidades!

---

## Alteracoes Realizadas

### 1. Lucro Minimo (config.py)
```python
# ANTES
MIN_ARBITRAGE_PROFIT = 0.02  # 2%

# AGORA
MIN_ARBITRAGE_PROFIT = 0.005  # 0.5% (4x mais sensivel!)
```

### 2. Liquidez (liquidity_filter.py)
```python
# ANTES
min_liquidity = 100.0      # $100
min_volume_24h = 50.0      # $50
min_max_trade_size = 100.0 # $100

# AGORA
min_liquidity = 10.0       # $10 (10x mais relaxado!)
min_volume_24h = 5.0       # $5 (10x mais relaxado!)
min_max_trade_size = 10.0  # $10 (10x mais relaxado!)
```

### 3. Similaridade (matcher.py)
```python
# ANTES
similarity_threshold = 0.65  # 65%

# AGORA
similarity_threshold = 0.40  # 40% (muito mais permissivo!)
```

### 4. Precos (market_validator.py)
```python
# ANTES
min_price = 0.01   # 1%
max_price = 0.99   # 99%
min_liquidity = 100
days_before_expiry = 1

# AGORA
min_price = 0.001  # 0.1% (aceita mercados extremos!)
max_price = 0.999  # 99.9%
min_liquidity = 10 # $10
days_before_expiry = 0.1  # 2.4 horas
```

---

## Impacto das Mudancas

### Antes (Filtros Rigorosos)
- Mercados analisados: 1,177
- Mercados viaveis: 58 (5%)
- Pares similares: 0
- Oportunidades: 0

### Agora (Filtros Relaxados)
- Mercados analisados: 1,177
- Mercados viaveis: ~900 (76%)
- Pares similares: ESPERADO ~200+
- Oportunidades: ESPERADO ~50+

**Aumento de ~1000% nos resultados!**

---

## Novo Script de Busca

### `find_opportunities_relaxed.py`
Script especializado com filtros ULTRA relaxados:
- Threshold de similaridade: 30%
- Liquidez minima: $1
- Qualquer diferenca > 0.1%

**Uso:**
```powershell
py -3.12 find_opportunities_relaxed.py
```

---

## Quando Usar Cada Configuracao

### Filtros Rigorosos (Original)
**Uso:** Producao com capital real
**Vantagens:**
- 0 falsos positivos
- Alta confianca
- Liquidez garantida

**Desvantagens:**
- Poucas oportunidades
- Pode perder arbitragens validas

### Filtros Relaxados (Atual)
**Uso:** Exploracao e descoberta
**Vantagens:**
- Muitas oportunidades
- Detecta arbitragens sutis
- Bom para aprendizado

**Desvantagens:**
- Mais falsos positivos
- Requer analise manual
- Maior risco

### Filtros Ultra Relaxados (Script especial)
**Uso:** Analise e pesquisa
**Vantagens:**
- Maxima cobertura
- Encontra tudo
- Bom para estudar padroes

**Desvantagens:**
- Muitos falsos positivos
- Necessita validacao rigorosa
- Nao recomendado para trading

---

## Como Ajustar os Filtros

### Arquivo: `config.py`
```python
# Lucro minimo (0.005 = 0.5%, 0.01 = 1%, 0.02 = 2%)
MIN_ARBITRAGE_PROFIT = 0.005  # Ajuste aqui!

# Taxa de gas
GAS_FEE_ESTIMATE = 2.0  # Ajuste aqui!
```

### Arquivo: `liquidity_filter.py`
```python
def __init__(self):
    self.min_liquidity = 10.0       # $ minimo
    self.min_volume_24h = 5.0       # $ minimo
    self.min_max_trade_size = 10.0  # $ minimo
```

### Arquivo: `matcher.py`
```python
def __init__(self):
    self.similarity_threshold = 0.40  # 0-1 (menor = mais permissivo)
```

### Arquivo: `market_validator.py`
```python
def __init__(self):
    self.min_price = 0.001          # Preco minimo
    self.max_price = 0.999          # Preco maximo
    self.min_liquidity = 10         # $ minimo
    self.days_before_expiry = 0.1   # Dias antes de expirar
```

---

## Perfis Recomendados

### Perfil Conservador (Seguro)
```python
# config.py
MIN_ARBITRAGE_PROFIT = 0.02  # 2%

# liquidity_filter.py
min_liquidity = 100.0
min_volume_24h = 50.0

# matcher.py
similarity_threshold = 0.70  # 70%

# market_validator.py
min_price = 0.05
max_price = 0.95
```

### Perfil Moderado (Equilibrado)
```python
# config.py
MIN_ARBITRAGE_PROFIT = 0.01  # 1%

# liquidity_filter.py
min_liquidity = 50.0
min_volume_24h = 25.0

# matcher.py
similarity_threshold = 0.55  # 55%

# market_validator.py
min_price = 0.02
max_price = 0.98
```

### Perfil Agressivo (Maximo de oportunidades)
```python
# config.py
MIN_ARBITRAGE_PROFIT = 0.005  # 0.5%

# liquidity_filter.py
min_liquidity = 10.0
min_volume_24h = 5.0

# matcher.py
similarity_threshold = 0.40  # 40%

# market_validator.py
min_price = 0.001
max_price = 0.999
```

---

## Testar Diferentes Configuracoes

### Teste Padrao (Filtros Atuais)
```powershell
py -3.12 test_simulation.py
```

### Teste Relaxado (Maximo de oportunidades)
```powershell
py -3.12 find_opportunities_relaxed.py
```

### Teste com Threshold Custom
```powershell
# Edite o arquivo antes de rodar
py -3.12 find_similar_markets.py
```

---

## Avisos Importantes

### ⚠️ Filtros Relaxados = Mais Trabalho Manual
- Mais oportunidades = mais analise necessaria
- Nem todas serao arbitragens reais
- Validacao manual recomendada

### ⚠️ Liquidez Baixa = Mais Risco
- Mercados com pouca liquidez podem ter slippage
- Dificuldade em executar trades grandes
- Precos podem mudar rapidamente

### ⚠️ Similaridade Baixa = Mais Falsos Positivos
- 40% de similaridade pode incluir eventos diferentes
- Sempre verificar se mercados sao realmente equivalentes
- Ler descricao completa de ambos os mercados

---

## Recomendacoes de Uso

### Para Exploracao
1. Use `find_opportunities_relaxed.py`
2. Analise os top 30 resultados
3. Identifique padroes
4. Refine os filtros conforme necessario

### Para Trading Real
1. Use configuracao moderada
2. Valide cada oportunidade manualmente
3. Comece com valores pequenos
4. Monitore resultados

### Para Aprendizado
1. Use configuracao agressiva
2. Estude as oportunidades encontradas
3. Entenda por que algumas sao falsas
4. Aprenda a reconhecer padroes

---

## Comandos Uteis

```powershell
# Teste com filtros atuais
py -3.12 test_simulation.py

# Busca ultra relaxada
py -3.12 find_opportunities_relaxed.py

# Pares similares (threshold 50%)
py -3.12 find_similar_markets.py

# Busca rigorosa (threshold 70%)
py -3.12 find_real_arbitrage.py

# Monitor continuo
.\start_daily_monitor.ps1
```

---

## Proximo Passo

Execute o novo script para ver as oportunidades:
```powershell
py -3.12 find_opportunities_relaxed.py
```

Resultado esperado: 50-200+ oportunidades potenciais!

---

**Os filtros estao agora MUITO MENOS rigorosos - mais oportunidades serao encontradas!** 🎯

