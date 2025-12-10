import React, { useState, useEffect, useMemo, useCallback } from 'react';
import '../theme.css';
import './DashboardModern.css';
import { 
  TrendingUp, 
  LogOut, 
  User, 
  DollarSign, 
  Activity, 
  Filter,
  Search,
  RefreshCw,
  AlertCircle,
  Clock,
  TrendingDown,
  BarChart3,
  ExternalLink,
  Sun,
  Moon,
  Radio
} from 'lucide-react';

const DashboardModern = ({ user, onLogout }) => {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [filters, setFilters] = useState({
    minProfit: 0,
    maxProfit: 100,
    search: '',
    exchange: 'all',
    sortBy: 'profit',
    arbitrageType: 'all' // 'all', 'combinatorial', 'traditional', 'probability', 'short_term'
  });
  const [showFilters, setShowFilters] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date()); // Para atualizar indicador em tempo real
  const [theme, setTheme] = useState(() => {
    // Carrega tema do localStorage ou usa 'dark' como padrão
    const savedTheme = localStorage.getItem('theme');
    return savedTheme || 'dark';
  });
  const [liveMode, setLiveMode] = useState(() => {
    // Carrega preferência de live mode do localStorage (padrão: ativado)
    const saved = localStorage.getItem('liveMode');
    return saved !== null ? saved === 'true' : true;
  });

  // Função para extrair título do mercado
  const extractTitle = (question) => {
    if (!question) return 'Oportunidade de Arbitragem';
    // Remove prefixos comuns e limpa o título
    let title = question
      .replace(/^(Will |Who will |What will |When will |How many |Which )/i, '')
      .replace(/\?.*$/, '')
      .replace(/ - (YES|NO|Republican|Democratic|Yes|No)$/i, '')
      .trim();
    // Capitaliza primeira letra
    return title.charAt(0).toUpperCase() + title.slice(1);
  };

  // Função para criar chave única de tema (para deduplicação)
  const getThemeKey = (opp) => {
    const question = opp.market1_question || opp.explanation || '';
    // Extrai o tema base removendo variações
    return question
      .toLowerCase()
      .replace(/\s+/g, ' ')
      .replace(/ - (yes|no|republican|democratic)$/i, '')
      .replace(/\?.*$/, '')
      .trim();
  };

  // Função para formatar data de conclusão
  const formatExpirationDate = (expiresAt) => {
    if (!expiresAt) return 'N/A';
    try {
      const date = new Date(expiresAt);
      if (isNaN(date.getTime())) return 'N/A';
      
      const now = new Date();
      const diffMs = date - now;
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      
      if (diffMs < 0) {
        return 'Expirado';
      } else if (diffDays > 0) {
        return `${diffDays}d ${diffHours}h`;
      } else if (diffHours > 0) {
        return `${diffHours}h`;
      } else {
        const diffMinutes = Math.floor(diffMs / (1000 * 60));
        return `${diffMinutes}min`;
      }
    } catch (e) {
      return 'N/A';
    }
  };

  // Função para obter data completa de conclusão
  const getExpirationDateFull = (opp) => {
    const expiresAt = opp.market1_expires_at || opp.market2_expires_at || opp.expires_at;
    if (!expiresAt) return null;
    try {
      const date = new Date(expiresAt);
      if (isNaN(date.getTime())) return null;
      return date;
    } catch (e) {
      return null;
    }
  };

  // Função para extrair informações detalhadas do mercado
  const getMarketDetails = (question, exchange, outcome, marketData = null) => {
    // Se marketData é um objeto Market completo, usa diretamente
    // Se tem full_data, usa full_data
    let actualMarketData = null;
    if (marketData) {
      if (marketData.full_data) {
        actualMarketData = marketData.full_data;
      } else if (marketData.market_id) {
        actualMarketData = marketData;
      }
    }
    const exchangeLower = (exchange || '').toLowerCase();
    
    // Para PredictIt: extrai o nome do contrato específico
    if (exchangeLower.includes('predictit')) {
      // Formato: "Question - ContractName"
      const parts = question.split(' - ');
      if (parts.length >= 2) {
        const contractName = parts[parts.length - 1].trim();
        // Remove "YES" ou "NO" do final se existir
        const cleanContract = contractName.replace(/\s+(YES|NO)$/i, '').trim();
        if (cleanContract) {
          return {
            contractName: cleanContract,
            baseQuestion: parts.slice(0, -1).join(' - '),
            option: cleanContract, // Mostra o nome do contrato como opção
            hasMultipleOptions: true,
            displayOption: `${cleanContract} (${outcome})` // Ex: "Republican (YES)"
          };
        }
      }
      // Fallback: usa outcome se não conseguir extrair
      return {
        contractName: null,
        baseQuestion: question,
        option: outcome,
        hasMultipleOptions: false,
        displayOption: outcome
      };
    }
    
    // Para Polymarket: sempre mostra YES/NO específico
    if (exchangeLower.includes('polymarket')) {
      // Polymarket sempre tem Yes/No, mas vamos garantir que está claro
      const optionText = outcome === 'YES' ? 'YES' : 'NO';
      return {
        contractName: null,
        baseQuestion: question,
        option: optionText,
        hasMultipleOptions: false,
        displayOption: optionText  // Sempre mostra YES ou NO claramente
      };
    }
    
    // Para Kalshi: extrai opção específica do subtitle ou market_id (igual PredictIt)
    if (exchangeLower.includes('kalshi')) {
      // Kalshi pode ter formato: "Question - Option Name" (ex: "Who will be the cover athlete? - Darryn Peterson")
      // O subtitle contém o nome específico da opção (atleta, candidato, etc.)
      // Formato similar ao PredictIt: "Question - ContractName"
      const parts = question.split(' - ');
      let optionName = null;
      let baseQuestion = question;
      
      if (parts.length >= 2) {
        // Tem subtitle na question - este é o nome específico da opção
        optionName = parts[parts.length - 1].trim(); // Ex: "Darryn Peterson", "Above 8%", "PPIZ"
        baseQuestion = parts.slice(0, -1).join(' - '); // Ex: "Who will be the cover athlete?"
        
        // Remove "YES" ou "NO" do final se existir (igual PredictIt)
        const cleanOption = optionName.replace(/\s+(YES|NO)$/i, '').trim();
        if (cleanOption) {
          optionName = cleanOption;
        }
        
        // Se encontrou um nome/opção no subtitle, usa ele (igual PredictIt)
        if (optionName && optionName.length > 0) {
          // Formato igual PredictIt: "OptionName (YES)" ou "OptionName (NO)"
          const displayText = `${optionName} (${outcome})`; // Ex: "Darryn Peterson (YES)" ou "Above 8% (NO)"
          
          return {
            contractName: optionName,  // Nome da opção específica (igual PredictIt)
            baseQuestion: baseQuestion,
            option: optionName,  // Opção específica (igual PredictIt)
            hasMultipleOptions: true,  // Kalshi tem múltiplas opções por mercado
            displayOption: displayText  // Mostra opção específica + YES/NO (igual PredictIt)
          };
        }
      }
      
      // Se não encontrou no subtitle, tenta extrair do market_id
      if (actualMarketData && actualMarketData.market_id) {
        // Tenta extrair do market_id (formato: TICKER-OPTION_YES/NO)
        // Ex: "KXNEWPOPE-70-PPIZ_YES" -> opção é "PPIZ"
        // Ex: "KXCOVER-DARRYN_YES" -> opção pode estar no ticker
        const marketIdParts = actualMarketData.market_id.split('_');
        if (marketIdParts.length >= 2) {
          const tickerPart = marketIdParts[0]; // "KXCOVER-DARRYN" ou "KXNEWPOPE-70-PPIZ"
          const tickerParts = tickerPart.split('-');
          
          // Se o ticker tem 3+ partes, a última geralmente é a opção
          if (tickerParts.length >= 3) {
            optionName = tickerParts[tickerParts.length - 1]; // "PPIZ" ou "DARRYN"
            // Tenta normalizar (capitalizar se for tudo maiúsculo)
            if (optionName === optionName.toUpperCase() && optionName.length > 2) {
              optionName = optionName.charAt(0) + optionName.slice(1).toLowerCase();
            }
          } else if (tickerParts.length === 2) {
            // Pode ser formato "KXCOVER-DARRYN" onde DARRYN é a opção
            const lastPart = tickerParts[1];
            if (lastPart.length > 2 && lastPart === lastPart.toUpperCase()) {
              optionName = lastPart.charAt(0) + lastPart.slice(1).toLowerCase();
            }
          }
        }
      }
      
      if (optionName && optionName.length > 0) {
        // YES = a opção específica acontece, NO = não acontece
        const displayText = outcome === 'YES' 
          ? `${optionName} (YES)`  // Ex: "Darryn Peterson (YES)" ou "Darryn (YES)"
          : `${optionName} (NO)`;   // Ex: "Darryn Peterson (NO)" ou "Darryn (NO)"
        
        return {
          contractName: optionName,  // Nome da opção específica
          baseQuestion: baseQuestion || question,
          option: optionName,  // Opção específica
          hasMultipleOptions: true,  // Kalshi tem múltiplas opções por mercado
          displayOption: displayText  // Mostra opção específica + YES/NO
        };
      }
      
      // Fallback: se não conseguiu extrair, verifica se a question indica múltiplas opções
      // Perguntas como "Who will..." geralmente têm múltiplas opções
      const hasMultipleOptionsQuestion = /^(who|which|what)\s+will/i.test(question) && 
                                        !question.includes(' - '); // Se não tem subtitle, pode ter múltiplas opções
      
      if (hasMultipleOptionsQuestion) {
        // Avisa que há múltiplas opções mas não conseguiu identificar qual
        return {
          contractName: null,
          baseQuestion: question,
          option: outcome,
          hasMultipleOptions: true,  // Indica que há múltiplas opções
          displayOption: `${outcome} (Múltiplas opções disponíveis - verificar link)`  // Avisa que precisa verificar
        };
      }
      
      // Fallback final: mostra apenas YES/NO
      return {
        contractName: null,
        baseQuestion: question,
        option: outcome,
        hasMultipleOptions: false,
        displayOption: outcome
      };
    }
    
    // Para Manifold: sempre YES/NO
    if (exchangeLower.includes('manifold')) {
      return {
        contractName: null,
        baseQuestion: question,
        option: outcome === 'YES' ? 'YES' : 'NO',
        hasMultipleOptions: false,
        displayOption: outcome === 'YES' ? 'YES' : 'NO'
      };
    }
    
    // Para outras exchanges: usa outcome padrão, mas tenta melhorar
    const parts = question.split(' - ');
    if (parts.length >= 2) {
      const lastPart = parts[parts.length - 1].trim();
      // Se não é apenas Yes/No, pode ser um outcome específico
      if (!/^(yes|no)$/i.test(lastPart)) {
        return {
          contractName: lastPart,
          baseQuestion: parts.slice(0, -1).join(' - '),
          option: lastPart,
          hasMultipleOptions: true,
          displayOption: `${lastPart} (${outcome})`
        };
      }
    }
    
    return {
      contractName: null,
      baseQuestion: question,
      option: outcome || 'YES',
      hasMultipleOptions: false,
      displayOption: outcome || 'YES'
    };
  };


  // Função para gerar passos de execução resumidos
  const generateExecutionSteps = (opp) => {
    const steps = [];
    const exchange1Name = opp.exchange1?.charAt(0).toUpperCase() + opp.exchange1?.slice(1) || 'Exchange 1';
    const exchange2Name = opp.exchange2?.charAt(0).toUpperCase() + opp.exchange2?.slice(1) || 'Exchange 2';
    
    if (opp.type === 'probability') {
      // Arbitragem por probabilidade (entre exchanges) - RESUMIDO
      const details1 = getMarketDetails(opp.market1_question, opp.exchange1, opp.market1_outcome, opp.market1_data);
      const details2 = getMarketDetails(opp.market2_question, opp.exchange2, opp.market2_outcome, opp.market2_data);
      
      steps.push(`📊 ESTRATÉGIA: Arbitragem por Spread de Probabilidade`);
      steps.push(`   Spread: ${(opp.spread_pct || 0).toFixed(2)}% | Lucro: ${(opp.profit_percent || 0).toFixed(2)}%`);
      steps.push(``);
      steps.push(`1️⃣ Comprar na ${exchange1Name}:`);
      steps.push(`   • Link: ${opp.market1_url || 'N/A'}`);
      steps.push(`   • Opção específica: ${details1.displayOption || details1.option}`);
      steps.push(`   • Preço: $${(opp.market1_price || opp.probability_low || 0).toFixed(2)}`);
      if (details1.hasMultipleOptions && details1.contractName) {
        steps.push(`   • ⚠️ IMPORTANTE: Selecione o contrato "${details1.contractName}"`);
      }
      steps.push(``);
      steps.push(`2️⃣ Vender na ${exchange2Name}:`);
      steps.push(`   • Link: ${opp.market2_url || 'N/A'}`);
      steps.push(`   • Opção específica: ${details2.displayOption || details2.option}`);
      steps.push(`   • Preço: $${(opp.market2_price || opp.probability_high || 0).toFixed(2)}`);
      if (details2.hasMultipleOptions && details2.contractName) {
        steps.push(`   • ⚠️ IMPORTANTE: Selecione o contrato "${details2.contractName}"`);
      }
      steps.push(``);
      steps.push(`3️⃣ Aguardar resolução para lucro garantido de ${(opp.profit_percent || 0).toFixed(2)}%`);
    } else if (opp.type === 'short_term') {
      // Arbitragem de curto prazo (trades rápidos/diários) - RESUMIDO
      const details1 = getMarketDetails(opp.market1_question, opp.exchange1, opp.market1_outcome, opp.market1_data);
      const details2 = getMarketDetails(opp.market2_question, opp.exchange2, opp.market2_outcome, opp.market2_data);
      
      steps.push(`⚡ ESTRATÉGIA: Arbitragem de Curto Prazo`);
      steps.push(`   ⏱️ Expira em ${(opp.time_to_expiry_hours || 0).toFixed(1)}h | Risco: ${opp.risk_level || 'médio'} | Lucro: ${(opp.profit_percent || 0).toFixed(2)}%`);
      steps.push(``);
      steps.push(`⚠️ ATENÇÃO: Execute rapidamente! Oportunidade pode desaparecer.`);
      steps.push(``);
      steps.push(`1️⃣ Comprar na ${exchange1Name}:`);
      steps.push(`   • Link: ${opp.market1_url || 'N/A'}`);
      steps.push(`   • Opção específica: ${details1.displayOption || details1.option}`);
      steps.push(`   • Preço: $${(opp.market1_price || opp.probability_low || 0).toFixed(2)}`);
      if (details1.hasMultipleOptions && details1.contractName) {
        steps.push(`   • ⚠️ IMPORTANTE: Selecione o contrato "${details1.contractName}"`);
      }
      steps.push(``);
      steps.push(`2️⃣ Vender na ${exchange2Name}:`);
      steps.push(`   • Link: ${opp.market2_url || 'N/A'}`);
      steps.push(`   • Opção específica: ${details2.displayOption || details2.option}`);
      steps.push(`   • Preço: $${(opp.market2_price || opp.probability_high || 0).toFixed(2)}`);
      if (details2.hasMultipleOptions && details2.contractName) {
        steps.push(`   • ⚠️ IMPORTANTE: Selecione o contrato "${details2.contractName}"`);
      }
      steps.push(``);
      steps.push(`3️⃣ Fechar posição antes da expiração ou aguardar resolução`);
    } else if (opp.type === 'combinatorial') {
      // Arbitragem combinatória (mesma exchange) - RESUMIDO
      const details1 = getMarketDetails(opp.market1_question, opp.exchange1, opp.market1_outcome, opp.market1_data);
      const details2 = getMarketDetails(opp.market2_question, opp.exchange2 || opp.exchange1, opp.market2_outcome, opp.market2_data);
      
      steps.push(`🧮 ESTRATÉGIA: Arbitragem Combinatória`);
      steps.push(`   Tipo: ${opp.strategy === 'complementary_buy' ? 'Comprar ambos' : 'Vender ambos'} | Lucro: ${(opp.profit_percent || 0).toFixed(2)}%`);
      steps.push(``);
      steps.push(`1️⃣ Acessar ${exchange1Name}:`);
      steps.push(`   • Link: ${opp.market1_url || 'N/A'}`);
      steps.push(`   • Mercado: "${opp.market1_question}"`);
      steps.push(``);
      if (opp.strategy === 'complementary_buy') {
        steps.push(`2️⃣ Comprar AMBAS as opções no mesmo mercado:`);
        steps.push(`   • Opção 1: ${details1.displayOption || details1.option} @ $${(opp.market1_price || 0).toFixed(2)}`);
        if (details1.hasMultipleOptions && details1.contractName) {
          steps.push(`     ⚠️ Selecione: "${details1.contractName}"`);
        }
        steps.push(`   • Opção 2: ${details2.displayOption || details2.option} @ $${(opp.market2_price || 0).toFixed(2)}`);
        if (details2.hasMultipleOptions && details2.contractName) {
          steps.push(`     ⚠️ Selecione: "${details2.contractName}"`);
        }
        steps.push(`   • Soma: ${(((opp.market1_price || 0) + (opp.market2_price || 0)) * 100).toFixed(1)}% < 100% → Lucro garantido`);
      } else {
        steps.push(`2️⃣ Vender AMBAS as opções no mesmo mercado:`);
        steps.push(`   • Opção 1: ${details1.displayOption || details1.option} @ $${(opp.market1_price || 0).toFixed(2)}`);
        if (details1.hasMultipleOptions && details1.contractName) {
          steps.push(`     ⚠️ Selecione: "${details1.contractName}"`);
        }
        steps.push(`   • Opção 2: ${details2.displayOption || details2.option} @ $${(opp.market2_price || 0).toFixed(2)}`);
        if (details2.hasMultipleOptions && details2.contractName) {
          steps.push(`     ⚠️ Selecione: "${details2.contractName}"`);
        }
        steps.push(`   • Soma: ${(((opp.market1_price || 0) + (opp.market2_price || 0)) * 100).toFixed(1)}% > 100% → Lucro garantido`);
      }
    } else {
      // Arbitragem tradicional (entre exchanges) - RESUMIDO
      const details1 = getMarketDetails(opp.market1_question, opp.exchange1, opp.market1_outcome, opp.market1_data);
      const details2 = getMarketDetails(opp.market2_question, opp.exchange2, opp.market2_outcome, opp.market2_data);
      
      steps.push(`🔄 ESTRATÉGIA: Arbitragem Tradicional`);
      steps.push(`   Diferença entre ${exchange1Name} e ${exchange2Name} | Lucro: ${(opp.profit_percent || 0).toFixed(2)}%`);
      steps.push(``);
      steps.push(`1️⃣ Comprar na ${exchange1Name} (preço menor):`);
      steps.push(`   • Link: ${opp.market1_url || 'N/A'}`);
      steps.push(`   • Opção específica: ${details1.displayOption || details1.option}`);
      steps.push(`   • Preço: $${(opp.market1_price || 0).toFixed(2)}`);
      if (details1.hasMultipleOptions && details1.contractName) {
        steps.push(`   • ⚠️ IMPORTANTE: Selecione o contrato "${details1.contractName}"`);
      }
      steps.push(``);
      steps.push(`2️⃣ Vender na ${exchange2Name} (preço maior):`);
      steps.push(`   • Link: ${opp.market2_url || 'N/A'}`);
      steps.push(`   • Opção específica: ${details2.displayOption || details2.option}`);
      steps.push(`   • Preço: $${(opp.market2_price || 0).toFixed(2)}`);
      if (details2.hasMultipleOptions && details2.contractName) {
        steps.push(`   • ⚠️ IMPORTANTE: Selecione o contrato "${details2.contractName}"`);
      }
      steps.push(``);
      steps.push(`3️⃣ Lucro garantido de ${(opp.profit_percent || 0).toFixed(2)}% após resolução`);
    }
    
    // Adiciona passos finais comuns
    steps.push(``);
    steps.push(`⚠️ VERIFICAÇÕES ANTES DE EXECUTAR:`);
    steps.push(`   • Liquidez mínima: $${(opp.market1_liquidity || 0).toFixed(0)} (${exchange1Name}) e $${(opp.market2_liquidity || 0).toFixed(0)} (${exchange2Name})`);
    steps.push(`   • Confirme que os mercados são equivalentes (mesmo evento/pergunta)`);
    steps.push(`   • Considere taxas de cada exchange (geralmente 2-5% por transação)`);
    steps.push(`   • Verifique datas de expiração (devem ser compatíveis)`);
    steps.push(``);
    steps.push(`✅ CONFIABILIDADE:`);
    steps.push(`   • Confiança no matching: ${((opp.confidence || 0) * 100).toFixed(0)}%`);
    steps.push(`   • Score de qualidade: ${(opp.quality_score || 0).toFixed(0)}/100`);
    
    return steps;
  };

  // Normaliza oportunidades do sistema especialista v2.0
  const normalizeOpportunity = (opp) => {
    const market1 = opp.markets?.[0] || {};
    const market2 = opp.markets?.[1] || {};
    
    return {
      // Identificação
      id: opp.id || `${Date.now()}-${Math.random()}`,
      type: opp.type || 'unknown',
      strategy: opp.strategy || 'unknown',
      
      // Métricas financeiras
      profit_percent: (opp.profit_pct || 0) * 100,
      profit_pct: opp.profit_pct || 0,
      gross_profit_pct: opp.gross_profit_pct || 0,
      total_investment: opp.total_investment || 0,
      expected_return: opp.expected_return || 0,
      spread_pct: (opp.spread_pct || 0) * 100,  // Spread de probabilidade
      probability_low: opp.probability_low || market1.price || 0,
      probability_high: opp.probability_high || market2.price || 0,
      net_profit: opp.net_profit || 0,
      
      // Dados específicos de curto prazo
      time_to_expiry_hours: opp.time_to_expiry_hours || 0,
      volatility_score: opp.volatility_score || 0,
      execution_speed: opp.execution_speed || 'médio',
      risk_level: opp.risk_level || 'médio',
      
      // Scores
      quality_score: opp.quality_score || 0,
      risk_score: opp.risk_score || 0,
      confidence: opp.confidence || 0,
      liquidity_score: opp.liquidity_score || 0,
      
      // Mercados
      exchange1: market1.exchange || 'N/A',
      exchange2: market2.exchange || market1.exchange || 'N/A',
      market1_question: market1.question || opp.explanation || 'N/A',
      market2_question: market2.question || opp.explanation || 'N/A',
      market1_price: market1.price || 0,
      market2_price: market2.price || 0,
      market1_liquidity: market1.liquidity || 0,
      market2_liquidity: market2.liquidity || 0,
      market1_outcome: market1.outcome || 'YES',
      market2_outcome: market2.outcome || 'NO',
      
      // URLs dos mercados
      market1_url: market1.url || null,
      market2_url: market2.url || null,
      
      // Datas de expiração
      market1_expires_at: market1.expires_at || opp.market1_expires_at || null,
      market2_expires_at: market2.expires_at || opp.market2_expires_at || null,
      expires_at: market1.expires_at || market2.expires_at || opp.expires_at || null,
      
      // Detalhes
      explanation: opp.explanation || '',
      execution_steps: opp.execution_steps || [],
      warnings: opp.warnings || [],
      
      // Raw markets para referência
      markets: opp.markets || []
    };
  };

  // Busca dados do backend (OTIMIZADO + TRATAMENTO DE ERRO)
  const fetchData = useCallback(async (showLoadingState = true) => {
    if (showLoadingState) setLoading(true);
    setError(null);

    try {
      // Busca apenas oportunidades (mais rápido)
      // Detecta se está em produção (GitHub Pages) ou desenvolvimento
      const API_URL = process.env.NODE_ENV === 'production' 
        ? 'https://predictionarb.onrender.com' // Backend em produção no Render
        : 'http://localhost:8000';
      
      const oppsResponse = await fetch(`${API_URL}/opportunities`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!oppsResponse.ok) {
        throw new Error(`Erro HTTP: ${oppsResponse.status}`);
      }

      const oppsData = await oppsResponse.json();

      // Atualiza oportunidades (tratamento seguro + normalização)
      const rawOpportunities = Array.isArray(oppsData.opportunities) 
        ? oppsData.opportunities 
        : (oppsData.opportunities ? [oppsData.opportunities] : []);
      
      // Normaliza todas as oportunidades
      const opportunities = rawOpportunities.map(normalizeOpportunity);
      
      setOpportunities(opportunities);
      setLastUpdate(oppsData.last_update ? new Date(oppsData.last_update) : new Date());
      
      // Cache local das oportunidades
      try {
        localStorage.setItem('cached_opportunities', JSON.stringify(opportunities));
        localStorage.setItem('cached_timestamp', new Date().toISOString());
      } catch (storageErr) {
        console.warn('Erro ao salvar cache:', storageErr);
      }
      
    } catch (err) {
      const errorMsg = err?.message || 'Erro desconhecido ao buscar dados';
      setError(errorMsg);
      console.error('Erro detalhado:', err);
      
      // Tenta usar cache local em caso de erro
      try {
        const cached = localStorage.getItem('cached_opportunities');
        if (cached) {
          const parsed = JSON.parse(cached);
          setOpportunities(Array.isArray(parsed) ? parsed : []);
        }
      } catch (cacheErr) {
        console.warn('Erro ao carregar cache:', cacheErr);
        setOpportunities([]);
      }
    } finally {
      if (showLoadingState) setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Carrega cache local primeiro (INSTANTÂNEO) - COM TRATAMENTO DE ERRO
    try {
      const cached = localStorage.getItem('cached_opportunities');
      const cachedTimestamp = localStorage.getItem('cached_timestamp');
      
      if (cached && cachedTimestamp) {
        const cacheAge = Date.now() - new Date(cachedTimestamp).getTime();
        // Se cache tem menos de 5 minutos, usa ele
        if (cacheAge < 5 * 60 * 1000) {
          const parsed = JSON.parse(cached);
          setOpportunities(Array.isArray(parsed) ? parsed : []);
          setLastUpdate(new Date(cachedTimestamp));
          setLoading(false);
          console.log('✓ Cache local carregado instantaneamente');
        }
      }
    } catch (err) {
      console.warn('Erro ao carregar cache inicial:', err);
      setOpportunities([]);
    }
    
    // Depois busca dados atualizados do servidor
    fetchData(true);
    
    // Atualiza indicador de tempo a cada segundo
    const timeInterval = setInterval(() => setCurrentTime(new Date()), 1000);
    
    return () => {
      clearInterval(timeInterval);
    };
  }, [fetchData]);

  // Efeito para atualizações automáticas quando live mode está ativado
  useEffect(() => {
    if (!liveMode) return; // Não atualiza se live mode estiver desativado
    
    // Atualiza silenciosamente a cada 20 segundos (sincronizado com backend)
    const interval = setInterval(() => fetchData(false), 20000);
    
    return () => {
      clearInterval(interval);
    };
  }, [liveMode, fetchData]);

  // Aplica tema ao documento
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Toggle de tema
  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  // Toggle de live mode
  const toggleLiveMode = () => {
    setLiveMode(prev => {
      const newValue = !prev;
      localStorage.setItem('liveMode', newValue.toString());
      return newValue;
    });
  };

  // Filtra, deduplica e ordena oportunidades (MEMOIZADO para performance)
  const filteredOpportunities = useMemo(() => {
    if (!opportunities || opportunities.length === 0) return [];
    
    let filtered = [...opportunities];

    // Filtro de tipo de arbitragem
    if (filters.arbitrageType !== 'all') {
      filtered = filtered.filter(opp => {
        if (filters.arbitrageType === 'combinatorial') {
          return opp.type === 'combinatorial';
        } else if (filters.arbitrageType === 'traditional') {
          return opp.type === 'traditional' || opp.type === 'classic';
        } else if (filters.arbitrageType === 'probability') {
          return opp.type === 'probability';
        } else if (filters.arbitrageType === 'short_term') {
          return opp.type === 'short_term';
        }
        return true;
      });
    }

    // Filtro de lucro
    filtered = filtered.filter(opp => {
      const profit = (opp.profit_pct || opp.profit_percent || 0) * 100;
      return profit >= filters.minProfit && profit <= filters.maxProfit;
    });

    // Filtro de busca
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(opp => {
        const q1 = (opp.buy?.question || opp.market1_question || '').toLowerCase();
        const q2 = (opp.sell?.question || opp.market2_question || '').toLowerCase();
        return q1.includes(searchLower) || q2.includes(searchLower);
      });
    }

    // Filtro de exchange
    if (filters.exchange !== 'all') {
      filtered = filtered.filter(opp => {
        const ex1 = opp.buy?.exchange || opp.exchange1 || '';
        const ex2 = opp.sell?.exchange || opp.exchange2 || '';
        return ex1 === filters.exchange || ex2 === filters.exchange;
      });
    }

    // Ordenação por lucro primeiro (para deduplicação pegar o melhor)
    filtered.sort((a, b) => {
      const profitA = (a.profit_pct || a.profit_percent || 0) * 100;
      const profitB = (b.profit_pct || b.profit_percent || 0) * 100;
      return profitB - profitA;
    });

    // DEDUPLICAÇÃO: Mantém apenas a melhor oportunidade por tema
    const seenThemes = new Map();
    const deduplicated = [];
    
    for (const opp of filtered) {
      const themeKey = getThemeKey(opp);
      
      if (!seenThemes.has(themeKey)) {
        seenThemes.set(themeKey, true);
        // Adiciona título extraído
        opp.title = extractTitle(opp.market1_question);
        deduplicated.push(opp);
      }
    }

    // Função auxiliar para calcular tempo até expiração (em horas)
    const getTimeToExpiry = (opp) => {
      // Para short_term, usa time_to_expiry_hours diretamente
      if (opp.type === 'short_term' && opp.time_to_expiry_hours) {
        return opp.time_to_expiry_hours;
      }
      
      // Para outras oportunidades, calcula a partir de expires_at
      // Tenta market1_expires_at primeiro, depois market2_expires_at, depois expires_at
      const expiresAt = opp.market1_expires_at || opp.market2_expires_at || opp.expires_at;
      if (expiresAt) {
        try {
          const expiryDate = new Date(expiresAt);
          // Verifica se a data é válida
          if (isNaN(expiryDate.getTime())) {
            return Infinity;
          }
          const now = new Date();
          const diffMs = expiryDate - now;
          const diffHours = diffMs / (1000 * 60 * 60);
          return diffHours > 0 ? diffHours : Infinity; // Retorna Infinity se já expirou
        } catch (e) {
          console.warn('Erro ao calcular tempo até expiração:', e, opp);
          return Infinity;
        }
      }
      
      // Se não tem data de expiração, retorna Infinity (vai para o final)
      return Infinity;
    };

    // Ordenação final
    deduplicated.sort((a, b) => {
      switch (filters.sortBy) {
        case 'profit':
          const profitA = (a.profit_pct || a.profit_percent || 0) * 100;
          const profitB = (b.profit_pct || b.profit_percent || 0) * 100;
          return profitB - profitA;
        case 'date':
          return new Date(b.market1_expires_at || 0) - new Date(a.market1_expires_at || 0);
        case 'expiry':
          // Ordena do mais próximo ao mais longe (menor tempo primeiro)
          const timeA = getTimeToExpiry(a);
          const timeB = getTimeToExpiry(b);
          if (timeA === Infinity && timeB === Infinity) return 0;
          if (timeA === Infinity) return 1; // Sem data vai para o final
          if (timeB === Infinity) return -1; // Sem data vai para o final
          // Debug: log para verificar ordenação
          if (timeA !== Infinity && timeB !== Infinity) {
            console.log(`Ordenando: ${a.title || a.market1_question} (${timeA.toFixed(1)}h) vs ${b.title || b.market1_question} (${timeB.toFixed(1)}h)`);
          }
          return timeA - timeB; // Menor tempo primeiro (mais próximo)
        case 'liquidity':
          const liqA = (a.market1_liquidity || 0) + (a.market2_liquidity || 0);
          const liqB = (b.market1_liquidity || 0) + (b.market2_liquidity || 0);
          return liqB - liqA;
        default:
          return 0;
      }
    });

    return deduplicated;
  }, [opportunities, filters]);

  // Estatísticas (OTIMIZADO)
  const stats = useMemo(() => {
    if (!opportunities || opportunities.length === 0) {
      return {
        totalOpportunities: 0,
        avgProfit: 0,
        totalMarkets: 0,
        bestProfit: 0
      };
    }

    const profits = opportunities.map(opp => (opp.profit_pct || opp.profit_percent || 0) * 100);
    
    // Contar mercados únicos das oportunidades
    const uniqueMarkets = new Set();
    opportunities.forEach(opp => {
      if (opp.market1?.id) uniqueMarkets.add(opp.market1.id);
      if (opp.market2?.id) uniqueMarkets.add(opp.market2.id);
    });
    
    return {
      totalOpportunities: opportunities.length,
      avgProfit: profits.reduce((sum, p) => sum + p, 0) / profits.length,
      totalMarkets: uniqueMarkets.size,
      bestProfit: Math.max(...profits, 0)
    };
  }, [opportunities]);

  const handleLogout = () => {
    localStorage.removeItem('user');
    onLogout();
  };

  return (
    <div className="dashboard-modern">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <div className="header-left">
            <TrendingUp size={32} className="logo-icon" />
            <div>
              <h1>Prediction Arbitrage</h1>
              <p className="header-subtitle">Dashboard em tempo real</p>
            </div>
          </div>

          <div className="header-right">
            <button 
              className={`btn-live ${liveMode ? 'active' : ''}`} 
              onClick={toggleLiveMode}
              title={liveMode ? 'Desativar atualizações automáticas' : 'Ativar atualizações automáticas'}
            >
              <Radio size={18} className={liveMode ? 'pulsing' : ''} />
              <span>{liveMode ? 'LIVE' : 'OFF'}</span>
            </button>

            <button className="btn-theme-toggle" onClick={toggleTheme} title={`Alternar para tema ${theme === 'dark' ? 'claro' : 'escuro'}`}>
              {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
            </button>

            <button className="btn-refresh" onClick={() => fetchData(true)} disabled={loading}>
              <RefreshCw size={18} className={loading ? 'spinning' : ''} />
              Atualizar
            </button>

            <div className="user-menu">
              <User size={20} />
              <span>{user?.name || 'Usuário'}</span>
              <button onClick={handleLogout} className="btn-logout">
                <LogOut size={18} />
              </button>
            </div>
          </div>
        </div>

        {lastUpdate && (
          <div className="last-update">
            <Clock size={14} />
            <span>Última atualização: {lastUpdate.toLocaleTimeString('pt-BR')}</span>
            <span className="update-indicator">
              {(() => {
                const secondsAgo = Math.floor((currentTime.getTime() - lastUpdate.getTime()) / 1000);
                if (secondsAgo < 25) {
                  return <span className="status-live">● AO VIVO</span>;
                } else if (secondsAgo < 60) {
                  return <span className="status-recent">Atualizado há {secondsAgo}s</span>;
                } else if (secondsAgo < 120) {
                  return <span className="status-recent">Atualizado há {Math.floor(secondsAgo / 60)}min</span>;
                } else {
                  return <span className="status-old">Atualizado há {Math.floor(secondsAgo / 60)}min</span>;
                }
              })()}
            </span>
          </div>
        )}
      </header>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon opportunities">
            <Activity />
          </div>
          <div className="stat-content">
            <h3>{stats.totalOpportunities}</h3>
            <p>Oportunidades Ativas</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon profit">
            <TrendingUp />
          </div>
          <div className="stat-content">
            <h3>{(stats.bestProfit || 0).toFixed(2)}%</h3>
            <p>Melhor Oportunidade</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon average">
            <BarChart3 />
          </div>
          <div className="stat-content">
            <h3>{(stats.avgProfit || 0).toFixed(2)}%</h3>
            <p>Lucro Médio</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon markets">
            <DollarSign />
          </div>
          <div className="stat-content">
            <h3>{stats.totalMarkets}</h3>
            <p>Mercados Monitorados</p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <button 
          className="btn-toggle-filters"
          onClick={() => setShowFilters(!showFilters)}
        >
          <Filter size={18} />
          {showFilters ? 'Ocultar' : 'Mostrar'} Filtros
        </button>

        {showFilters && (
          <div className="filters-panel">
            <div className="filter-group">
              <label>
                <Search size={16} />
                Buscar
              </label>
              <input
                type="text"
                placeholder="Buscar por mercado..."
                value={filters.search}
                onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              />
            </div>

            <div className="filter-group">
              <label>Lucro Mínimo (%)</label>
              <input
                type="number"
                value={filters.minProfit}
                onChange={(e) => setFilters({ ...filters, minProfit: Number(e.target.value) })}
                min="0"
                max="100"
              />
            </div>

            <div className="filter-group">
              <label>Lucro Máximo (%)</label>
              <input
                type="number"
                value={filters.maxProfit}
                onChange={(e) => setFilters({ ...filters, maxProfit: Number(e.target.value) })}
                min="0"
                max="100"
              />
            </div>

            <div className="filter-group">
              <label>Tipo de Arbitragem</label>
              <select 
                value={filters.arbitrageType}
                onChange={(e) => setFilters({ ...filters, arbitrageType: e.target.value })}
              >
                <option value="all">Todos os Tipos</option>
                <option value="combinatorial">🧮 Combinatória (mesma exchange)</option>
                <option value="probability">📊 Por Probabilidade (entre exchanges)</option>
                <option value="short_term">⚡ Curto Prazo (trades rápidos/diários)</option>
                <option value="traditional">🔄 Tradicional (clássica)</option>
              </select>
            </div>

            <div className="filter-group">
              <label>Exchange</label>
              <select 
                value={filters.exchange}
                onChange={(e) => setFilters({ ...filters, exchange: e.target.value })}
              >
                <option value="all">Todas</option>
                <option value="kalshi">Kalshi</option>
                <option value="polymarket">Polymarket</option>
                <option value="predictit">PredictIt</option>
                <option value="manifold">Manifold</option>
              </select>
            </div>

            <div className="filter-group">
              <label>Ordenar por</label>
              <select 
                value={filters.sortBy}
                onChange={(e) => setFilters({ ...filters, sortBy: e.target.value })}
              >
                <option value="profit">Maior Lucro</option>
                <option value="expiry">⏱️ Tempo até Expiração (mais próximo primeiro)</option>
                <option value="date">Data de Expiração</option>
                <option value="liquidity">Maior Liquidez</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="dashboard-content">
        {error && (
          <div className="alert alert-error">
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        )}

        {loading && opportunities.length === 0 ? (
          <div className="loading-state">
            <RefreshCw size={48} className="spinning" />
            <p>Carregando oportunidades...</p>
          </div>
        ) : filteredOpportunities.length === 0 ? (
          <div className="empty-state">
            <TrendingDown size={64} />
            <h3>Nenhuma oportunidade encontrada</h3>
            <p>Ajuste os filtros ou aguarde novos dados</p>
          </div>
        ) : (
          <div className="opportunities-grid">
            {filteredOpportunities.map((opp, index) => (
              <div key={opp.id || index} className={`opportunity-card ${opp.type}`}>
                {/* Título da oportunidade */}
                <div className="opportunity-title">
                  <h3>{opp.title || extractTitle(opp.market1_question)}</h3>
                </div>

                {/* Header com lucro e tipo */}
                <div className="opportunity-header">
                  <div className="profit-badge">
                    <TrendingUp size={16} />
                    +{(opp.profit_percent || 0).toFixed(2)}%
                  </div>
                  <div className="type-badge" title={opp.strategy}>
                    {opp.type === 'combinatorial' ? '🧮' : opp.type === 'probability' ? '📊' : opp.type === 'short_term' ? '⚡' : opp.type === 'traditional' ? '🔄' : '⚖️'}
                    {opp.type === 'combinatorial' ? 'Combinatória' : opp.type === 'probability' ? 'Por Probabilidade' : opp.type === 'short_term' ? 'Curto Prazo' : opp.type === 'traditional' ? 'Tradicional' : opp.strategy?.replace('_', ' ')}
                  </div>
                </div>

                {/* Scores */}
                <div className="scores-row">
                  <div className="score" title="Qualidade geral">
                    <span className="score-label">Score</span>
                    <span className={`score-value ${opp.quality_score > 50 ? 'high' : opp.quality_score > 25 ? 'medium' : 'low'}`}>
                      {(opp.quality_score || 0).toFixed(0)}
                    </span>
                  </div>
                  <div className="score" title="Confiança">
                    <span className="score-label">Conf.</span>
                    <span className="score-value">{((opp.confidence || 0) * 100).toFixed(0)}%</span>
                  </div>
                  <div className="score" title="Risco (menor = melhor)">
                    <span className="score-label">Risco</span>
                    <span className={`score-value ${opp.risk_score < 0.3 ? 'low' : opp.risk_score < 0.6 ? 'medium' : 'high'}`}>
                      {((opp.risk_score || 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>

                {/* Exchanges */}
                <div className="exchanges-row">
                  <span className={`exchange-badge ${opp.exchange1 || 'unknown'}`}>
                    {opp.exchange1 || 'N/A'}
                  </span>
                  {opp.exchange1 !== opp.exchange2 && (
                    <>
                      <span className="arrow">→</span>
                      <span className={`exchange-badge ${opp.exchange2 || 'unknown'}`}>
                        {opp.exchange2 || 'N/A'}
                      </span>
                    </>
                  )}
                </div>

                {/* Explicação */}
                <div className="opportunity-body">
                  <p className="explanation">
                    {opp.explanation || 'Oportunidade de arbitragem detectada'}
                  </p>

                  {/* Detalhes financeiros */}
                  <div className="opportunity-details">
                    {/* Data de Conclusão - Sempre visível */}
                    {(() => {
                      const expiryDate = getExpirationDateFull(opp);
                      const timeToExpiry = opp.type === 'short_term' && opp.time_to_expiry_hours 
                        ? `${opp.time_to_expiry_hours.toFixed(1)}h` 
                        : formatExpirationDate(opp.market1_expires_at || opp.market2_expires_at || opp.expires_at);
                      
                      return (
                        <div className="detail-row expiration-row">
                          <span className="label">📅 Data de Conclusão:</span>
                          <span className="value expiration-value">
                            {expiryDate ? (
                              <>
                                <span className="expiration-time">{timeToExpiry}</span>
                                <span className="expiration-date">
                                  ({expiryDate.toLocaleDateString('pt-BR', { 
                                    day: '2-digit', 
                                    month: '2-digit', 
                                    year: 'numeric',
                                    hour: '2-digit',
                                    minute: '2-digit'
                                  })})
                                </span>
                              </>
                            ) : (
                              <span>N/A</span>
                            )}
                          </span>
                        </div>
                      );
                    })()}
                    
                    {opp.type === 'short_term' ? (
                      <>
                        <div className="detail-row">
                          <span className="label">⏱️ Tempo até Expiração:</span>
                          <span className="value">{opp.time_to_expiry_hours ? `${opp.time_to_expiry_hours.toFixed(1)}h` : 'N/A'}</span>
                        </div>
                        <div className="detail-row">
                          <span className="label">🚀 Velocidade de Execução:</span>
                          <span className={`value ${opp.execution_speed === 'rápido' ? 'buy' : opp.execution_speed === 'médio' ? 'medium' : 'sell'}`}>
                            {opp.execution_speed || 'médio'}
                          </span>
                        </div>
                        <div className="detail-row">
                          <span className="label">⚠️ Nível de Risco:</span>
                          <span className={`value ${opp.risk_level === 'baixo' ? 'buy' : opp.risk_level === 'médio' ? 'medium' : 'sell'}`}>
                            {opp.risk_level || 'médio'}
                          </span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Spread de Probabilidade:</span>
                          <span className="value buy">{(opp.spread_pct || 0).toFixed(2)}%</span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Probabilidade Baixa:</span>
                          <span className="value">{(opp.probability_low || 0) * 100}%</span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Probabilidade Alta:</span>
                          <span className="value">{(opp.probability_high || 0) * 100}%</span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Lucro Líquido ($100):</span>
                          <span className="value buy">${(opp.net_profit || 0).toFixed(2)}</span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Score de Volatilidade:</span>
                          <span className="value">{(opp.volatility_score || 0).toFixed(2)}</span>
                        </div>
                      </>
                    ) : opp.type === 'probability' && opp.spread_pct ? (
                      <>
                        <div className="detail-row">
                          <span className="label">Spread de Probabilidade:</span>
                          <span className="value buy">{(opp.spread_pct || 0).toFixed(2)}%</span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Probabilidade Baixa:</span>
                          <span className="value">{(opp.probability_low || 0) * 100}%</span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Probabilidade Alta:</span>
                          <span className="value buy">{(opp.probability_high || 0) * 100}%</span>
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="detail-row">
                          <span className="label">Investimento:</span>
                          <span className="value">${(opp.total_investment || 0).toFixed(3)}</span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Retorno:</span>
                          <span className="value buy">${(opp.expected_return || 0).toFixed(3)}</span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Liquidez:</span>
                          <span className={`value ${opp.liquidity_score > 0.5 ? 'high' : 'low'}`}>
                            {opp.liquidity_score > 0.8 ? '🟢 Alta' : opp.liquidity_score > 0.4 ? '🟡 Média' : '🔴 Baixa'}
                          </span>
                        </div>
                      </>
                    )}
                  </div>

                  {/* Warnings */}
                  {opp.warnings && opp.warnings.length > 0 && (
                    <div className="warnings">
                      {opp.warnings.slice(0, 2).map((warning, i) => (
                        <span key={i} className="warning-tag">{warning}</span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Links para os mercados com informações detalhadas */}
                <div className="market-links">
                  {opp.market1_url && (() => {
                    const details1 = getMarketDetails(opp.market1_question, opp.exchange1, opp.market1_outcome, opp.market1_data);
                    return (
                      <a 
                        href={opp.market1_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className={`market-link ${opp.exchange1}`}
                        title={`${details1.baseQuestion} - ${details1.displayOption || details1.option}`}
                      >
                        <ExternalLink size={14} />
                        <div className="link-content">
                          <div className="link-header">
                            <span className="link-exchange">{opp.exchange1}</span>
                            <span className="link-action">COMPRAR</span>
                          </div>
                          <div className="link-details">
                            <span className="link-option" title={details1.displayOption || details1.option}>
                              {details1.displayOption || details1.option}
                            </span>
                            <span className="link-price">${(opp.market1_price || 0).toFixed(2)}</span>
                          </div>
                          {details1.hasMultipleOptions && details1.contractName && (
                            <div className="link-note">
                              📋 Opção específica: {details1.contractName}
                            </div>
                          )}
                          {!details1.hasMultipleOptions && (
                            <div className="link-note">
                              📋 Tipo: {details1.option === 'YES' ? 'Yes' : details1.option === 'NO' ? 'No' : details1.option}
                            </div>
                          )}
                        </div>
                      </a>
                    );
                  })()}
                  {opp.market2_url && opp.market2_url !== opp.market1_url && (() => {
                    const details2 = getMarketDetails(opp.market2_question, opp.exchange2, opp.market2_outcome, opp.market2_data);
                    return (
                      <a 
                        href={opp.market2_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className={`market-link ${opp.exchange2}`}
                        title={`${details2.baseQuestion} - ${details2.displayOption || details2.option}`}
                      >
                        <ExternalLink size={14} />
                        <div className="link-content">
                          <div className="link-header">
                            <span className="link-exchange">{opp.exchange2}</span>
                            <span className="link-action">VENDER</span>
                          </div>
                          <div className="link-details">
                            <span className="link-option" title={details2.displayOption || details2.option}>
                              {details2.displayOption || details2.option}
                            </span>
                            <span className="link-price">${(opp.market2_price || 0).toFixed(2)}</span>
                          </div>
                          {details2.hasMultipleOptions && details2.contractName && (
                            <div className="link-note">
                              📋 Opção específica: {details2.contractName}
                            </div>
                          )}
                          {!details2.hasMultipleOptions && (
                            <div className="link-note">
                              📋 Tipo: {details2.option === 'YES' ? 'Yes' : details2.option === 'NO' ? 'No' : details2.option}
                            </div>
                          )}
                        </div>
                      </a>
                    );
                  })()}
                </div>

                {/* Footer com passos */}
                <div className="opportunity-footer">
                  <details className="execution-steps">
                    <summary>
                      📋 Ver passos de execução
                      {opp.execution_steps && opp.execution_steps.length > 0 
                        ? ` (${opp.execution_steps.length})` 
                        : ` (${generateExecutionSteps(opp).length})`}
                    </summary>
                    <ol>
                      {(opp.execution_steps && opp.execution_steps.length > 0 
                        ? opp.execution_steps 
                        : generateExecutionSteps(opp)
                      ).map((step, i) => {
                        const isWarning = step.includes('⚠️');
                        const isSuccess = step.includes('✅');
                        const isSection = step.includes('📊') || step.includes('🧮') || step.includes('🔄');
                        const isStep = step.includes('1️⃣') || step.includes('2️⃣') || step.includes('3️⃣');
                        const isEmpty = step.trim() === '';
                        const stepNumber = isStep ? step.match(/[1-3]️⃣/)?.[0]?.replace('️⃣', '') : null;
                        
                        return (
                          <li 
                            key={i}
                            data-type={
                              isEmpty ? undefined :
                              isWarning ? 'warning' : 
                              isSuccess ? 'success' : 
                              isSection ? 'section' :
                              isStep ? 'step' : undefined
                            }
                            data-step-number={stepNumber || undefined}
                          >
                            {step}
                          </li>
                        );
                      })}
                    </ol>
                  </details>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardModern;


