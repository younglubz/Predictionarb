# 🚀 Prediction Market Arbitrage Dashboard

Dashboard moderno para identificar oportunidades de arbitragem entre os principais protocolos de prediction markets.

## ✨ Funcionalidades

- **Dashboard em Tempo Real**: Visualização de oportunidades de arbitragem atualizadas automaticamente
- **Múltiplas Exchanges**: Suporte para Polymarket, PredictIt, Kalshi e Augur
- **Análise de Arbitragem**: Detecção automática de discrepâncias de preços entre exchanges
- **Interface Moderna**: UI responsiva e intuitiva com gráficos e visualizações
- **WebSocket**: Atualizações em tempo real via WebSocket
- **Estatísticas**: Métricas detalhadas de volume, liquidez e oportunidades

## 🏗️ Arquitetura

### Backend (Python/FastAPI)
- **API REST**: Endpoints para oportunidades, mercados e estatísticas
- **WebSocket**: Atualizações em tempo real
- **Integrações**: Conecta com APIs reais dos protocolos de prediction markets
- **Engine de Arbitragem**: Algoritmo para detectar oportunidades lucrativas

### Frontend (React)
- **Dashboard Interativo**: Visualização de dados com gráficos
- **Lista de Oportunidades**: Cards detalhados com informações de arbitragem
- **Lista de Mercados**: Busca e filtros por exchange
- **Estatísticas**: Painel com métricas gerais

## 📦 Instalação

### Pré-requisitos
- Python 3.8+
- Node.js 16+
- npm ou yarn

### Backend

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o servidor:
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

1. Navegue até a pasta do frontend:
```bash
cd frontend
```

2. Instale as dependências:
```bash
npm install
```

3. Execute o servidor de desenvolvimento:
```bash
npm start
```

O dashboard estará disponível em `http://localhost:3000`

## 🔌 APIs Suportadas

### Polymarket
- API: `https://clob.polymarket.com`
- Protocolo: REST/GraphQL
- Status: ✅ Implementado

### PredictIt
- API: `https://www.predictit.org/api`
- Protocolo: REST
- Status: ✅ Implementado

### Kalshi
- API: `https://trading-api.kalshi.com/trade-api/v2`
- Protocolo: REST
- Status: ✅ Implementado

### Augur
- API: `https://api.augur.net`
- Protocolo: REST
- Status: ✅ Implementado

## 📡 Endpoints da API

### GET `/`
Informações gerais da API

### GET `/opportunities`
Lista todas as oportunidades de arbitragem detectadas

### GET `/markets`
Lista todos os mercados de todas as exchanges

### GET `/stats`
Estatísticas gerais (volume, liquidez, contagens)

### WebSocket `/ws`
Conexão WebSocket para atualizações em tempo real

## 🎯 Como Funciona

1. **Coleta de Dados**: O sistema busca mercados ativos de todas as exchanges conectadas
2. **Matching**: Algoritmo de similaridade identifica eventos equivalentes entre exchanges
3. **Análise de Arbitragem**: Calcula diferenças de preço, taxas e lucro líquido
4. **Filtragem**: Apenas oportunidades com lucro mínimo e liquidez suficiente são exibidas
5. **Atualização**: Dados são atualizados automaticamente a cada 30 segundos

## ⚙️ Configuração

Edite `config.py` para ajustar:
- `MIN_ARBITRAGE_PROFIT`: Lucro mínimo necessário (padrão: 2%)
- `MIN_LIQUIDITY`: Liquidez mínima em USD (padrão: $100)
- `UPDATE_INTERVAL`: Intervalo de atualização em segundos (padrão: 30)
- `EXCHANGE_FEES`: Taxas por exchange
- `GAS_FEES`: Taxas de gas para blockchains

## 🎨 Screenshots

O dashboard inclui:
- Painel de estatísticas com métricas principais
- Gráficos de oportunidades por exchange
- Lista detalhada de oportunidades com informações de compra/venda
- Lista de mercados com busca e filtros
- Indicador de conexão WebSocket em tempo real

## 🔒 Segurança

- As APIs são públicas e não requerem autenticação
- Não armazena dados sensíveis
- Apenas leitura de dados públicos das exchanges

## 🚧 Limitações

- As APIs podem ter rate limits
- Algumas exchanges podem exigir autenticação para dados completos
- Matching de eventos pode ter falsos positivos
- Taxas de gas podem variar

## 📝 Licença

Este projeto é open source e está disponível para uso livre.

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 📧 Suporte

Para questões ou sugestões, abra uma issue no repositório.

