"""Modulo de exchanges"""
from exchanges.polymarket import PolymarketExchange
from exchanges.predictit import PredictItExchange
from exchanges.predictit_v2 import PredictItV2Exchange
from exchanges.kalshi import KalshiExchange
from exchanges.kalshi_v2 import KalshiV2Exchange
from exchanges.augur import AugurExchange
from exchanges.manifold import ManifoldExchange
from exchanges.azuro import AzuroExchange
from exchanges.omen import OmenExchange
from exchanges.seer import SeerExchange
from exchanges.base import ExchangeBase, Market

__all__ = ["PolymarketExchange", "PredictItExchange", "PredictItV2Exchange",
           "KalshiExchange", "KalshiV2Exchange", "AugurExchange", "ManifoldExchange",
           "AzuroExchange", "OmenExchange", "SeerExchange",
           "ExchangeBase", "Market"]

