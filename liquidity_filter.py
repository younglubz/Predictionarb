"""
Módulo de Filtragem de Liquidez, Volume e Spread

Garante que só consideramos mercados com condições adequadas para arbitragem:
- Liquidez suficiente para executar trades
- Volume adequado (mercado ativo)
- Spread aceitável (diferença bid-ask)
"""
from typing import List, Optional
from exchanges.base import Market
from dataclasses import dataclass


@dataclass
class LiquidityRequirements:
    """Requisitos minimos de liquidez (RELAXADOS)"""
    min_liquidity: float = 20.0  # USD (reduzido de 100)
    min_volume_24h: float = 10.0  # USD (reduzido de 50)
    max_spread_pct: float = 0.10  # 10% (aumentado de 5%)
    min_trade_size: float = 5.0  # USD (reduzido de 10)


class LiquidityFilter:
    """
    Filtra mercados baseado em liquidez, volume e spread
    
    Critérios:
    1. Liquidez mínima - garantir que há fundos suficientes
    2. Volume 24h mínimo - mercado precisa ser ativo
    3. Spread máximo - diferença bid-ask não pode ser muito alta
    4. Tamanho mínimo de trade - viabilidade econômica
    """
    
    def __init__(self, requirements: Optional[LiquidityRequirements] = None):
        self.requirements = requirements or LiquidityRequirements()
    
    def check_liquidity(self, market: Market) -> tuple[bool, str]:
        """
        Verifica se mercado tem liquidez suficiente
        
        Returns:
            Tuple[bool, str]: (passa_no_filtro, motivo_se_falhou)
        """
        if market.liquidity < self.requirements.min_liquidity:
            return False, f"Liquidez insuficiente: ${market.liquidity:.2f} < ${self.requirements.min_liquidity:.2f}"
        
        return True, ""
    
    def check_volume(self, market: Market) -> tuple[bool, str]:
        """
        Verifica se mercado tem volume adequado
        
        Returns:
            Tuple[bool, str]: (passa_no_filtro, motivo_se_falhou)
        """
        if market.volume_24h < self.requirements.min_volume_24h:
            return False, f"Volume 24h insuficiente: ${market.volume_24h:.2f} < ${self.requirements.min_volume_24h:.2f}"
        
        return True, ""
    
    def calculate_max_trade_size(self, market: Market, safety_factor: float = 0.1) -> float:
        """
        Calcula tamanho máximo de trade sem afetar significativamente o preço
        
        Args:
            market: Mercado a analisar
            safety_factor: Fator de segurança (10% = usar apenas 10% da liquidez)
        
        Returns:
            float: Tamanho máximo de trade em USD
        """
        # Usa o menor entre liquidez e volume
        available = min(market.liquidity, market.volume_24h * 0.5)
        
        # Aplica fator de segurança
        max_size = available * safety_factor
        
        return max_size
    
    def filter_market(self, market: Market) -> tuple[bool, list[str]]:
        """
        Aplica todos os filtros em um mercado
        
        Returns:
            Tuple[bool, List[str]]: (passou_nos_filtros, lista_de_problemas)
        """
        issues = []
        
        # 1. Liquidez
        liquidity_ok, liquidity_msg = self.check_liquidity(market)
        if not liquidity_ok:
            issues.append(liquidity_msg)
        
        # 2. Volume
        volume_ok, volume_msg = self.check_volume(market)
        if not volume_ok:
            issues.append(volume_msg)
        
        # 3. Preço válido (não resolvido)
        if market.price >= 0.99 or market.price <= 0.01:
            issues.append(f"Mercado já resolvido ou certeza absoluta: ${market.price:.3f}")
        
        # 4. Tamanho mínimo viável
        max_trade = self.calculate_max_trade_size(market)
        if max_trade < self.requirements.min_trade_size:
            issues.append(f"Trade máximo muito pequeno: ${max_trade:.2f} < ${self.requirements.min_trade_size:.2f}")
        
        passed = len(issues) == 0
        return passed, issues
    
    def filter_markets(self, markets: List[Market]) -> tuple[List[Market], dict]:
        """
        Filtra lista de mercados
        
        Returns:
            Tuple[List[Market], dict]: (mercados_válidos, estatísticas)
        """
        valid_markets = []
        stats = {
            "total": len(markets),
            "passed": 0,
            "failed": 0,
            "reasons": {}
        }
        
        for market in markets:
            passed, issues = self.filter_market(market)
            
            if passed:
                valid_markets.append(market)
                stats["passed"] += 1
            else:
                stats["failed"] += 1
                for issue in issues:
                    # Extrai categoria do problema
                    category = issue.split(":")[0]
                    stats["reasons"][category] = stats["reasons"].get(category, 0) + 1
        
        return valid_markets, stats
    
    def calculate_spread(self, buy_price: float, sell_price: float) -> float:
        """
        Calcula spread percentual entre dois preços
        
        Args:
            buy_price: Preço de compra
            sell_price: Preço de venda
        
        Returns:
            float: Spread como percentual (0.05 = 5%)
        """
        if buy_price <= 0:
            return 1.0
        
        spread = abs(sell_price - buy_price) / buy_price
        return spread
    
    def is_arbitrage_viable(
        self,
        market_buy: Market,
        market_sell: Market,
        min_profit_pct: float = 0.02
    ) -> tuple[bool, dict]:
        """
        Verifica se arbitragem é viável considerando liquidez
        
        Args:
            market_buy: Mercado para comprar
            market_sell: Mercado para vender
            min_profit_pct: Lucro mínimo requerido
        
        Returns:
            Tuple[bool, dict]: (é_viável, análise_detalhada)
        """
        analysis = {
            "viable": False,
            "max_trade_size": 0.0,
            "expected_profit_pct": 0.0,
            "expected_profit_usd": 0.0,
            "issues": []
        }
        
        # 1. Verifica liquidez de ambos os mercados
        buy_ok, buy_msg = self.filter_market(market_buy)
        sell_ok, sell_msg = self.filter_market(market_sell)
        
        if not buy_ok:
            analysis["issues"].extend(["Mercado de compra: " + i for i in buy_msg])
        
        if not sell_ok:
            analysis["issues"].extend(["Mercado de venda: " + i for i in sell_msg])
        
        if not (buy_ok and sell_ok):
            return False, analysis
        
        # 2. Calcula tamanho máximo de trade
        max_buy = self.calculate_max_trade_size(market_buy)
        max_sell = self.calculate_max_trade_size(market_sell)
        max_trade = min(max_buy, max_sell)
        
        analysis["max_trade_size"] = max_trade
        
        if max_trade < self.requirements.min_trade_size:
            analysis["issues"].append(f"Trade máximo muito pequeno: ${max_trade:.2f}")
            return False, analysis
        
        # 3. Calcula lucro esperado
        price_diff = market_sell.price - market_buy.price
        profit_pct = price_diff / market_buy.price if market_buy.price > 0 else 0
        
        # Considera taxas
        from config import EXCHANGE_FEES
        fee_buy = EXCHANGE_FEES.get(market_buy.exchange.split('_')[0], 0.02)
        fee_sell = EXCHANGE_FEES.get(market_sell.exchange.split('_')[0], 0.02)
        total_fees = fee_buy + fee_sell
        
        net_profit_pct = profit_pct - total_fees
        net_profit_usd = max_trade * net_profit_pct
        
        analysis["expected_profit_pct"] = net_profit_pct
        analysis["expected_profit_usd"] = net_profit_usd
        
        # 4. Verifica se lucro é suficiente
        if net_profit_pct < min_profit_pct:
            analysis["issues"].append(
                f"Lucro insuficiente: {net_profit_pct:.2%} < {min_profit_pct:.2%}"
            )
            return False, analysis
        
        # Se passou em todos os checks
        analysis["viable"] = True
        return True, analysis

