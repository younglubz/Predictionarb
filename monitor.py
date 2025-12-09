"""Monitor em tempo real de oportunidades de arbitragem"""
import asyncio
from typing import List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime
from exchanges.base import Market
from exchanges import (PolymarketExchange, PredictItV2Exchange, KalshiV2Exchange,
                       AugurExchange, ManifoldExchange, AzuroExchange, 
                       OmenExchange, SeerExchange, PolyRouterExchange)
from matcher_improved import ImprovedEventMatcher
from arbitrage import ArbitrageEngine, ArbitrageOpportunity
from arbitrage_combinatorial import CombinatorialArbitrage, CombinatorialOpportunity
from arbitrage_probability import ProbabilityArbitrageEngine, ProbabilityArbitrageOpportunity
from arbitrage_short_term import ShortTermArbitrageEngine, ShortTermArbitrageOpportunity
from email_notifier import EmailNotifier
from config import UPDATE_INTERVAL


class ArbitrageMonitor:
    """Monitor contínuo de arbitragem"""
    
    def __init__(self):
        self.console = Console()
        self.exchanges = [
            PolyRouterExchange(),  # API agregada - PRIORIDADE
            PolymarketExchange(),  # Fonte original
            ManifoldExchange(),
            PredictItV2Exchange(), # PredictIt (CFTC regulada)
            KalshiV2Exchange(),    # Kalshi Demo API (CFTC regulada)
            # AzuroExchange(),  # Esportes - desabilitado
            # OmenExchange(),   # Gnosis Chain - desabilitado
            # SeerExchange(),   # Gnosis Chain - desabilitado
            # AugurExchange(),  # API descontinuada
        ]
        self.matcher = ImprovedEventMatcher(similarity_threshold=0.55, max_date_diff_days=21)
        self.engine = ArbitrageEngine()
        self.combinatorial = CombinatorialArbitrage()  # Arbitragem combinatória
        self.probability_engine = ProbabilityArbitrageEngine(self.matcher)  # Arbitragem por probabilidade
        self.short_term_engine = ShortTermArbitrageEngine(self.matcher)  # Arbitragem de curto prazo
        self.last_update = None
        self.opportunities: List[ArbitrageOpportunity] = []
        self.combinatorial_opportunities: List[CombinatorialOpportunity] = []
        self.probability_opportunities: List[ProbabilityArbitrageOpportunity] = []
        self.short_term_opportunities: List[ShortTermArbitrageOpportunity] = []  # NOVO
        self._cached_markets: List[Market] = []  # Cache de mercados
    
    async def fetch_all_markets(self) -> List[Market]:
        """Busca mercados de todas as exchanges em paralelo com timeout"""
        all_markets = []
        
        # Executa todas as exchanges em paralelo com timeout de 10s cada
        tasks = [exchange.fetch_markets() for exchange in self.exchanges]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for exchange, result in zip(self.exchanges, results):
            if isinstance(result, list):
                all_markets.extend(result)
                self.console.print(f"[green]{exchange.__class__.__name__}: {len(result)} mercados[/green]")
            elif isinstance(result, Exception):
                self.console.print(f"[red]{exchange.__class__.__name__} erro: {result}[/red]")
        
        return all_markets
    
    async def update(self):
        """Atualiza dados e encontra oportunidades (OTIMIZADO)"""
        start_time = datetime.now()
        self.console.print("[yellow]Atualizando mercados...[/yellow]")
        
        # 1. Busca mercados em paralelo
        markets = await self.fetch_all_markets()
        self._cached_markets = markets  # Atualiza cache
        self.console.print(f"[green]✓ Encontrados {len(markets)} mercados em {(datetime.now() - start_time).total_seconds():.1f}s[/green]")
        
        # 2. Encontra matches (rápido - só compara strings)
        match_start = datetime.now()
        matches = self.matcher.find_matching_events(markets)
        self.console.print(f"[green]✓ Encontrados {len(matches)} pares em {(datetime.now() - match_start).total_seconds():.1f}s[/green]")
        
        # 3. Calcula confiança (otimizado - cache interno do matcher)
        confidence_start = datetime.now()
        market_pairs = []
        for market1, market2 in matches:
            confidence = self.matcher.calculate_enhanced_similarity(
                market1.question,
                market2.question
            )
            market_pairs.append((market1, market2, confidence))
        self.console.print(f"[green]✓ Confiança calculada em {(datetime.now() - confidence_start).total_seconds():.1f}s[/green]")
        
        # 4. Encontra oportunidades tradicionais (rápido - só calcula lucros)
        opp_start = datetime.now()
        self.opportunities = self.engine.find_opportunities(market_pairs)
        self.console.print(f"[green]✓ {len(self.opportunities)} oportunidades tradicionais em {(datetime.now() - opp_start).total_seconds():.1f}s[/green]")
        
        # 5. Arbitragem combinatória (Yes/No, relacionados)
        comb_start = datetime.now()
        self.combinatorial_opportunities = self.combinatorial.find_all_opportunities(markets)
        self.console.print(f"[green]✓ {len(self.combinatorial_opportunities)} oportunidades combinatórias em {(datetime.now() - comb_start).total_seconds():.1f}s[/green]")
        
        # 6. Arbitragem por probabilidade (compara % entre exchanges)
        prob_start = datetime.now()
        self.probability_opportunities = self.probability_engine.find_opportunities(markets)
        self.console.print(f"[green]✓ {len(self.probability_opportunities)} oportunidades por probabilidade em {(datetime.now() - prob_start).total_seconds():.1f}s[/green]")
        
        # 7. NOVO: Arbitragem de curto prazo (trades rápidos/diários)
        short_start = datetime.now()
        self.short_term_opportunities = self.short_term_engine.find_opportunities(markets)
        self.console.print(f"[green]✓ {len(self.short_term_opportunities)} oportunidades de curto prazo em {(datetime.now() - short_start).total_seconds():.1f}s[/green]")
        
        self.last_update = datetime.now()
        total_time = (self.last_update - start_time).total_seconds()
        total_opps = len(self.opportunities) + len(self.combinatorial_opportunities) + len(self.probability_opportunities) + len(self.short_term_opportunities)
        self.console.print(f"[bold green]✓ TOTAL: {total_opps} oportunidades em {total_time:.1f}s[/bold green]")
    
    def render_dashboard(self) -> Table:
        """Renderiza dashboard de oportunidades"""
        table = Table(title="🚀 Oportunidades de Arbitragem")
        
        table.add_column("Lucro", justify="right", style="green")
        table.add_column("Comprar", style="cyan")
        table.add_column("Vender", style="magenta")
        table.add_column("Confiança", justify="right")
        table.add_column("Liquidez", justify="right")
        
        if not self.opportunities:
            table.add_row("Nenhuma oportunidade encontrada", "", "", "", "")
        else:
            for opp in self.opportunities[:10]:  # Top 10
                table.add_row(
                    f"{opp.profit_pct:.2%}",
                    f"{opp.market_buy.exchange} @ ${opp.buy_price:.4f}",
                    f"{opp.market_sell.exchange} @ ${opp.sell_price:.4f}",
                    f"{opp.confidence:.1%}",
                    f"${min(opp.market_buy.liquidity, opp.market_sell.liquidity):.0f}"
                )
        
        return table
    
    async def run(self):
        """Executa monitor contínuo"""
        self.console.print("[bold green]Iniciando monitor de arbitragem...[/bold green]")
        
        # Primeira atualização
        await self.update()
        
        # Loop de atualização
        while True:
            try:
                await self.update()
                
                # Mostra dashboard
                dashboard = self.render_dashboard()
                info_panel = Panel(
                    f"Última atualização: {self.last_update.strftime('%H:%M:%S') if self.last_update else 'N/A'}\n"
                    f"Oportunidades encontradas: {len(self.opportunities)}",
                    title="Status"
                )
                
                self.console.clear()
                self.console.print(dashboard)
                self.console.print(info_panel)
                
                # Mostra detalhes das top 3 oportunidades
                if self.opportunities:
                    self.console.print("\n[bold]Top 3 Oportunidades:[/bold]")
                    for i, opp in enumerate(self.opportunities[:3], 1):
                        self.console.print(Panel(str(opp), title=f"#{i}"))
                
                await asyncio.sleep(UPDATE_INTERVAL)
            
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Monitor interrompido pelo usuário[/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]Erro: {e}[/red]")
                await asyncio.sleep(UPDATE_INTERVAL)

