# 📅 Guia do Monitor Diário de Arbitragem

## ✅ O Que Foi Implementado

### 1. **3 Novas Exchanges Adicionadas**
- **Azuro** (`exchanges/azuro.py`) - Focado em esportes via The Graph
- **Omen** (`exchanges/omen.py`) - Gnosis Chain via The Graph
- **Seer** (`exchanges/seer.py`) - Gnosis Chain

### 2. **Monitor Diário Automático**
- **Arquivo**: `daily_monitor.py`
- **Funcionalidade**: Verifica oportunidades automaticamente em horários programados
- **Horários**: 09:00, 15:00, 21:00 (3x por dia)
- **Log**: Salva resultados em `arbitrage_log.jsonl`

### 3. **Script de Início Automático**
- **Arquivo**: `start_daily_monitor.ps1`
- **Funcionalidade**: Inicia o monitor em segundo plano

## 🚀 Como Usar

### Opção 1: Monitor Automático (Recomendado)

```powershell
.\start_daily_monitor.ps1
```

Isso vai:
1. Verificar dependências
2. Executar verificação inicial imediatamente
3. Agendar verificações para 09:00, 15:00 e 21:00
4. Rodar continuamente (deixe aberto)

### Opção 2: Verificação Manual Única

```powershell
py -3.12 find_real_opportunities.py
```

Executa uma verificação única e mostra resultados no terminal.

## 📊 Status Atual das Exchanges

| Exchange | Status | Mercados | Observação |
|----------|--------|----------|------------|
| **Polymarket** | ✅ Funcionando | 74 | Filtrado (resolvidos removidos) |
| **Manifold** | ✅ Funcionando | 192 | API pública estável |
| **Azuro** | ⚠️ Implementado | 0 | The Graph - precisa testar endpoint |
| **Omen** | ⚠️ Implementado | 0 | The Graph - pode estar offline |
| **Seer** | ⚠️ Implementado | 0 | API precisa verificação |
| PredictIt | ❌ Não funciona | 0 | API inválida |
| Kalshi | ❌ Não funciona | 0 | API mudou |
| Augur | ❌ Descontinuado | 0 | Projeto inativo |

## 📝 Sistema de Logs

### Arquivo: `arbitrage_log.jsonl`

Cada verificação gera uma entrada no formato:

```json
{
  "timestamp": "2025-01-09T15:00:00",
  "total_markets": 266,
  "by_exchange": {
    "polymarket": 74,
    "manifold": 192
  },
  "similar_pairs": 0,
  "opportunities": 0,
  "details": []
}
```

### Analisar Logs

```powershell
# Ver últimas 10 verificações
Get-Content arbitrage_log.jsonl -Tail 10 | ConvertFrom-Json | Format-List

# Contar total de oportunidades encontradas
(Get-Content arbitrage_log.jsonl | ConvertFrom-Json | Measure-Object -Property opportunities -Sum).Sum
```

## 🎯 Quando Esperar Oportunidades

### Alta Probabilidade
- **Eleições presidenciais** (múltiplas exchanges cobrem)
- **Super Bowl / Copa do Mundo** (esportes aparecem em várias)
- **Oscars / Grammy** (entretenimento)
- **Debates políticos** (ao vivo)

### Média Probabilidade
- **Jogos NBA/NFL** (Polymarket + Azuro se ativar)
- **Eventos cripto** (Polymarket + exchanges Web3)
- **Lançamentos produtos** (Apple, Tesla)

### Baixa Probabilidade
- Dias normais sem grandes eventos
- Mercados muito nichados
- Horários de baixa atividade (madrugada)

## ⚙️ Configurações

### Alterar Horários de Verificação

Edite `daily_monitor.py`:

```python
# Linha ~110
schedule.every().day.at("09:00").do(run_daily_check)
schedule.every().day.at("15:00").do(run_daily_check)
schedule.every().day.at("21:00").do(run_daily_check)

# Adicionar mais horários:
schedule.every().day.at("12:00").do(run_daily_check)
schedule.every().day.at("18:00").do(run_daily_check)
```

### Alterar Threshold de Similaridade

Edite `config.py`:

```python
# Mais flexível (mais matches, mas menos precisos)
MIN_ARBITRAGE_PROFIT = 0.005  # 0.5%

# Mais restritivo (menos matches, mas mais precisos)
MIN_ARBITRAGE_PROFIT = 0.02  # 2%
```

### Adicionar Notificações

Edite `daily_monitor.py` na função `check_opportunities()`:

```python
if opportunities:
    # Adicionar notificação por email/telegram/discord
    send_notification(f"🚨 {len(opportunities)} oportunidades encontradas!")
```

## 📈 Melhorias Futuras

### Curto Prazo
1. ✅ Monitor automático (FEITO)
2. ⏳ Notificações (email/telegram)
3. ⏳ Dashboard web de logs históricos
4. ⏳ Ativar Azuro/Omen/Seer

### Médio Prazo
1. ⏳ Adicionar Opinion, Limitless, Myriad
2. ⏳ WebSocket real-time (mais rápido)
3. ⏳ Machine Learning para prever oportunidades
4. ⏳ Backtesting com dados históricos

### Longo Prazo
1. ⏳ Execução automática de trades
2. ⏳ Market making
3. ⏳ Integração com wallets
4. ⏳ Mobile app

## 🔧 Troubleshooting

### "Nenhuma oportunidade encontrada"
- **Normal**: Oportunidades são raras
- **Solução**: Deixar rodando por dias/semanas
- **Aumentar chances**: Adicionar mais exchanges

### "Exchange retorna 0 mercados"
- **Possível causa**: API offline ou mudou
- **Solução**: Verificar documentação da API
- **Alternativa**: Remover exchange temporariamente

### "Script para de rodar"
- **Possível causa**: Erro não tratado
- **Solução**: Verificar logs de erro
- **Workaround**: Reiniciar automaticamente via task scheduler

## 📞 Suporte

### Arquivos Importantes
- `daily_monitor.py` - Monitor automático
- `find_real_opportunities.py` - Verificação manual
- `arbitrage_log.jsonl` - Histórico de verificações
- `RELATORIO_ARBITRAGEM.md` - Análise detalhada

### Comandos Úteis

```powershell
# Testar exchanges individualmente
py -3.12 test_exchanges.py

# Ver configurações
cat config.py

# Limpar logs antigos
Remove-Item arbitrage_log.jsonl

# Verificar processos rodando
Get-Process python
```

---

**Sistema pronto para rodar 24/7 e encontrar oportunidades automaticamente!** 🚀

