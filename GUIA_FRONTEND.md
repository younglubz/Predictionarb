# Guia do Frontend Interativo

## Sistema de Dashboard com Filtros e Interacoes

O frontend agora possui um sistema completo de filtros, navegacao por tabs e exportacao de dados!

---

## Novos Recursos

### 1. Painel de Filtros Interativos

#### **Filtros Disponiveis:**
- **Lucro Minimo (%)**: Filtra oportunidades por ROI minimo
- **Liquidez Minima ($)**: Filtra por liquidez disponivel
- **Exchange**: Filtra por exchange especifica
- **Ordenar Por**: Ordena resultados (lucro/liquidez)

#### **Filtros Rapidos:**
- 🟢 **Relaxado**: 0.5% lucro, $20 liquidez
- 🟡 **Moderado**: 1% lucro, $50 liquidez
- 🔴 **Rigoroso**: 2% lucro, $100 liquidez

### 2. Navegacao por Tabs

- **🎯 Oportunidades**: Lista de arbitragens encontradas
- **📊 Mercados**: Todos os mercados monitorados
- **📈 Estatisticas**: Metricas detalhadas e graficos

### 3. Botoes de Acao

- **🔄 Atualizar**: Recarrega dados manualmente
- **📥 Exportar**: Baixa dados em JSON

### 4. Estatisticas Expandidas

- Metricas por exchange
- Analise de oportunidades
- Lucro total potencial
- Distribuicao de mercados

---

## Como Usar

### Iniciar Sistema

```powershell
# 1. Iniciar Backend
py -3.12 run_server.py

# 2. Iniciar Frontend (novo terminal)
cd frontend
npm start

# 3. Acessar
# http://localhost:3000
```

### Usar Filtros

1. **Ajustar Lucro Minimo:**
   - Digite valor desejado (ex: 0.5 para 0.5%)
   - Sistema filtra automaticamente

2. **Ajustar Liquidez:**
   - Digite valor em dolares (ex: 100)
   - Mostra apenas mercados com liquidez suficiente

3. **Selecionar Exchange:**
   - Escolha exchange especifica
   - Ou "Todas" para ver tudo

4. **Filtros Rapidos:**
   - Clique em um dos 3 botoes
   - Aplica configuracao pre-definida

### Navegar por Tabs

1. **Oportunidades**:
   - Lista de arbitragens
   - Mostra lucro potencial
   - Links para exchanges

2. **Mercados**:
   - Todos os mercados disponiveis
   - Busca e filtro
   - Detalhes de cada mercado

3. **Estatisticas**:
   - Metricas gerais
   - Distribuicao por exchange
   - Graficos e analises

### Exportar Dados

1. Clique em **📥 Exportar**
2. Arquivo JSON e baixado
3. Contem:
   - Oportunidades filtradas
   - Mercados filtrados
   - Estatisticas
   - Data de exportacao

---

## Estrutura de Arquivos

```
frontend/
├── src/
│   ├── App.js                     # App principal (versao atual)
│   ├── App_enhanced.js           # App melhorado (nova versao!)
│   ├── App.css                   # Estilos principais
│   ├── components/
│   │   ├── FilterPanel.js       # 🆕 Painel de filtros
│   │   ├── FilterPanel.css      # 🆕 Estilos do painel
│   │   ├── StatsPanel.js        # Estatisticas (atualizado)
│   │   ├── StatsPanel.css       # Estilos (atualizado)
│   │   ├── Dashboard.js
│   │   ├── OpportunitiesList.js
│   │   └── MarketsList.js
│   └── ErrorBoundary.js
```

---

## Para Usar a Versao Melhorada

### Opcao 1: Substituir App.js

```powershell
# Backup do original
Copy-Item frontend/src/App.js frontend/src/App_original.js

# Usar versao melhorada
Copy-Item frontend/src/App_enhanced.js frontend/src/App.js -Force
```

### Opcao 2: Editar App.js Manualmente

Adicione ao topo:
```javascript
import FilterPanel from './components/FilterPanel';
```

Adicione states:
```javascript
const [activeTab, setActiveTab] = useState('opportunities');
const [filters, setFilters] = useState({
  minProfit: 0,
  minLiquidity: 0,
  exchange: 'all',
  sortBy: 'profit'
});
```

Adicione logica de filtragem:
```javascript
const filteredOpportunities = opportunities.filter(opp => {
  if (filters.minProfit > 0 && opp.roi < filters.minProfit) return false;
  if (filters.exchange !== 'all' && 
      opp.exchange_a !== filters.exchange && 
      opp.exchange_b !== filters.exchange) return false;
  return true;
});
```

---

## CSS Adicional

### Botoes de Acao

```css
.header-actions {
  display: flex;
  gap: 10px;
}

.btn-primary {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-primary:hover {
  background: #45a049;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #2196F3;
  color: white;
  /* ... resto igual */
}
```

### Tabs de Navegacao

```css
.nav-tabs {
  display: flex;
  background: white;
  max-width: 1200px;
  margin: 0 auto;
  border-radius: 12px 12px 0 0;
}

.tab {
  flex: 1;
  padding: 15px 20px;
  border: none;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.tab-active {
  background: #f0f7ff;
  border-bottom: 3px solid #4CAF50;
  color: #4CAF50;
}
```

---

## Funcionalidades por Componente

### FilterPanel

**Props:**
- `filters`: Object com filtros atuais
- `setFilters`: Funcao para atualizar filtros

**Funcoes:**
- `updateFilter(key, value)`: Atualiza um filtro
- `resetFilters()`: Limpa todos os filtros

**Features:**
- Validacao de valores
- Feedback visual
- Filtros rapidos
- Contador de filtros ativos

### StatsPanel Expandido

**Props:**
- `stats`: Estatisticas gerais
- `opportunities`: Lista de oportunidades
- `markets`: Lista de mercados

**Mostra:**
- Stats principais
- Distribuicao por exchange
- Metricas de oportunidades
- Analise detalhada

### App Enhanced

**States:**
- `activeTab`: Tab atual selecionada
- `filters`: Filtros ativos
- `opportunities`: Lista original
- `filteredOpportunities`: Lista filtrada

**Funcoes:**
- `handleRefresh()`: Recarrega dados
- `handleExport()`: Exporta para JSON
- `loadData()`: Carrega da API

---

## Exemplos de Uso

### Filtrar Oportunidades > 2%

1. Acesse tab "Oportunidades"
2. Digite "2" em "Lucro Minimo"
3. Sistema filtra automaticamente

### Ver Apenas Polymarket

1. Selecione "Polymarket" no dropdown "Exchange"
2. Tabs mostram contadores atualizados

### Exportar Dados Filtrados

1. Aplique filtros desejados
2. Clique em "📥 Exportar"
3. JSON baixado com dados filtrados

### Usar Filtro Rapido

1. Clique em "🟢 Relaxado"
2. Aplica: 0.5% lucro, $20 liquidez
3. Resultados aparecem instantaneamente

---

## Troubleshooting

### Filtros nao funcionam

**Solucao:**
- Verificar se `FilterPanel` esta importado
- Verificar se states estao declarados
- Verificar logica de filtragem no App.js

### Tabs nao aparecem

**Solucao:**
- Adicionar CSS para `.nav-tabs`
- Verificar se `activeTab` state existe
- Verificar imports de componentes

### Botoes sem estilo

**Solucao:**
- Adicionar CSS para `.btn-primary` e `.btn-secondary`
- Verificar se App.css esta importado
- Limpar cache do navegador

### Exportacao nao funciona

**Solucao:**
- Verificar permissoes do navegador para downloads
- Verificar funcao `handleExport()`
- Testar em navegador diferente

---

## Performance

### Otimizacoes Implementadas

- Filtragem eficiente (O(n))
- Atualizacao seletiva de componentes
- Lazy loading de tabs
- Memoizacao de dados filtrados

### Dicas de Performance

1. **Limitar resultados exibidos:**
```javascript
const displayedOpps = filteredOpportunities.slice(0, 50);
```

2. **Debounce em filtros:**
```javascript
const debouncedFilter = useDebounce(filters, 300);
```

3. **Virtualizacao de listas longas:**
```javascript
// Usar react-window para listas >100 items
```

---

## Proximos Passos

### Melhorias Planejadas

1. **Graficos Interativos:**
   - Usar Chart.js ou Recharts
   - Graficos de linha (historico)
   - Graficos de pizza (distribuicao)

2. **Busca Avancada:**
   - Busca por texto
   - Filtros combinados
   - Regex support

3. **Alertas no Browser:**
   - Notificacoes push
   - Alertas sonoros
   - Configuracao de thresholds

4. **Tema Escuro:**
   - Toggle dark/light
   - Persistencia em localStorage
   - CSS variables

5. **Mobile Responsive:**
   - Layout adaptativo
   - Touch gestures
   - Menu hamburger

---

## Atalhos de Teclado (Futuro)

| Atalho | Acao |
|--------|------|
| `Ctrl + R` | Atualizar dados |
| `Ctrl + E` | Exportar |
| `Ctrl + 1` | Tab Oportunidades |
| `Ctrl + 2` | Tab Mercados |
| `Ctrl + 3` | Tab Estatisticas |
| `Ctrl + F` | Focar em busca |
| `ESC` | Limpar filtros |

---

**Frontend interativo completo e pronto para uso profissional!** 🚀

