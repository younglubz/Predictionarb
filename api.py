"""FastAPI backend para dashboard de arbitragem"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse
from typing import List, Dict
import asyncio
import json
import time
from datetime import datetime
from monitor import ArbitrageMonitor
from arbitrage import ArbitrageOpportunity
from exchanges.base import Market
from paper_trading import PaperTradingEngine
from market_validator import MarketValidator
from arbitrage_expert import ArbitrageExpert, ArbitrageOpportunityV2

app = FastAPI(title="Prediction Market Arbitrage API")

# Compressao GZIP para respostas grandes (reduz tamanho em 70%)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS para permitir frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache simples em memoria
_cache = {}
_cache_time = {}

def get_cached(key: str, ttl: int = 30):
    """Retorna valor do cache se ainda valido"""
    if key in _cache and key in _cache_time:
        if time.time() - _cache_time[key] < ttl:
            return _cache[key]
    return None

def set_cache(key: str, value):
    """Armazena valor no cache"""
    _cache[key] = value
    _cache_time[key] = time.time()

# Instância global do monitor
monitor = ArbitrageMonitor()
expert = ArbitrageExpert()  # Sistema especialista v2.0
connected_clients: List[WebSocket] = []

# Cache de oportunidades do sistema especialista
_expert_opportunities = []
_expert_last_update = None

# Engine de paper trading
paper_trading = PaperTradingEngine(initial_balance=10000.0)
validator = MarketValidator()


async def broadcast_update():
    """Envia atualização para todos os clientes conectados"""
    if not connected_clients:
        return
    
    data = {
        "opportunities": [serialize_opportunity(opp) for opp in monitor.opportunities],
        "last_update": monitor.last_update.isoformat() if monitor.last_update else None,
    }
    
    message = json.dumps(data)
    disconnected = []
    
    for client in connected_clients:
        try:
            await client.send_text(message)
        except:
            disconnected.append(client)
    
    # Remove clientes desconectados
    for client in disconnected:
        if client in connected_clients:
            connected_clients.remove(client)


def serialize_opportunity(opp: ArbitrageOpportunity) -> Dict:
    """Serializa oportunidade para JSON"""
    # Valida equivalência
    equivalent, validation = validator.validate_equivalence(opp.market_buy, opp.market_sell)
    
    return {
        "profit_pct": opp.profit_pct,
        "profit_abs": opp.profit_abs,
        "net_profit": opp.net_profit,
        "fees": opp.fees,
        "confidence": opp.confidence,
        "validated": equivalent,
        "validation_details": {
            "confidence": validation.get("confidence", 0),
            "issues": validation.get("issues", [])
        },
        "buy": {
            "exchange": opp.market_buy.exchange,
            "price": opp.buy_price,
            "question": opp.market_buy.question,
            "liquidity": opp.market_buy.liquidity,
            "url": opp.market_buy.url
        },
        "sell": {
            "exchange": opp.market_sell.exchange,
            "price": opp.sell_price,
            "question": opp.market_sell.question,
            "liquidity": opp.market_sell.liquidity,
            "url": opp.market_sell.url
        }
    }


def serialize_combinatorial_opportunity(opp) -> Dict:
    """Serializa oportunidade combinatória para JSON"""
    return {
        "type": "combinatorial",
        "strategy": opp.strategy,
        "profit_pct": opp.expected_profit_pct,
        "confidence": opp.confidence,
        "explanation": opp.explanation,
        "total_probability": opp.total_probability,
        "risk_score": getattr(opp, 'risk_score', 0.0),
        "liquidity_score": getattr(opp, 'liquidity_score', 0.0),
        "quality_score": getattr(opp, 'quality_score', 0.0),
        "risk_level": getattr(opp, 'risk_level', 'médio'),
        "markets": [
            {
                "exchange": m.exchange,
                "question": m.question,
                "outcome": m.outcome,
                "price": m.price,
                "url": m.url,
                "liquidity": m.liquidity,
                "expires_at": m.expires_at.isoformat() if m.expires_at else None,
                "market_id": m.market_id
            }
            for m in opp.markets
        ]
    }

def serialize_probability_opportunity(opp) -> Dict:
    """Serializa oportunidade de arbitragem por probabilidade para JSON"""
    return {
        "type": "probability",
        "strategy": "probability_spread",
        "profit_pct": opp.profit_pct,
        "profit_abs": opp.profit_abs,
        "net_profit": opp.net_profit,
        "fees": opp.fees,
        "confidence": opp.confidence,
        "spread_pct": opp.spread_pct,
        "probability_low": opp.probability_low,
        "probability_high": opp.probability_high,
        "risk_score": getattr(opp, 'risk_score', 0.0),
        "liquidity_score": getattr(opp, 'liquidity_score', 0.0),
        "quality_score": getattr(opp, 'quality_score', 0.0),
        "risk_level": getattr(opp, 'risk_level', 'médio'),
        "explanation": opp.explanation,
        "markets": [
            {
                "exchange": opp.market_low.exchange,
                "question": opp.market_low.question,
                "outcome": opp.market_low.outcome,
                "price": opp.probability_low,
                "url": opp.market_low.url,
                "liquidity": opp.market_low.liquidity,
                "expires_at": opp.market_low.expires_at.isoformat() if opp.market_low.expires_at else None,
                "market_id": opp.market_low.market_id,
                "full_data": {
                    "exchange": opp.market_low.exchange,
                    "market_id": opp.market_low.market_id,
                    "question": opp.market_low.question,
                    "outcome": opp.market_low.outcome,
                    "price": opp.probability_low,
                    "volume_24h": opp.market_low.volume_24h,
                    "liquidity": opp.market_low.liquidity,
                    "expires_at": opp.market_low.expires_at.isoformat() if opp.market_low.expires_at else None,
                    "url": opp.market_low.url
                }
            },
            {
                "exchange": opp.market_high.exchange,
                "question": opp.market_high.question,
                "outcome": opp.market_high.outcome,
                "price": opp.probability_high,
                "url": opp.market_high.url,
                "liquidity": opp.market_high.liquidity,
                "expires_at": opp.market_high.expires_at.isoformat() if opp.market_high.expires_at else None,
                "market_id": opp.market_high.market_id,
                "full_data": {
                    "exchange": opp.market_high.exchange,
                    "market_id": opp.market_high.market_id,
                    "question": opp.market_high.question,
                    "outcome": opp.market_high.outcome,
                    "price": opp.probability_high,
                    "volume_24h": opp.market_high.volume_24h,
                    "liquidity": opp.market_high.liquidity,
                    "expires_at": opp.market_high.expires_at.isoformat() if opp.market_high.expires_at else None,
                    "url": opp.market_high.url
                }
            }
        ]
    }


def serialize_short_term_opportunity(opp) -> Dict:
    """Serializa oportunidade de arbitragem de curto prazo para JSON"""
    return {
        "type": "short_term",
        "strategy": "short_term_trade",
        "profit_pct": opp.profit_pct,
        "profit_abs": opp.profit_abs,
        "net_profit": opp.net_profit,
        "fees": opp.fees,
        "confidence": opp.confidence,
        "spread_pct": opp.spread_pct,
        "probability_low": opp.probability_low,
        "probability_high": opp.probability_high,
        "time_to_expiry_hours": opp.time_to_expiry_hours,
        "volatility_score": opp.volatility_score,
        "execution_speed": opp.execution_speed,
        "risk_level": opp.risk_level,
        "risk_score": getattr(opp, 'risk_score', 0.0),
        "liquidity_score": getattr(opp, 'liquidity_score', 0.0),
        "quality_score": getattr(opp, 'quality_score', 0.0),
        "explanation": opp.explanation,
        "markets": [
            {
                "exchange": opp.market_low.exchange,
                "question": opp.market_low.question,
                "outcome": opp.market_low.outcome,
                "price": opp.probability_low,
                "url": opp.market_low.url,
                "liquidity": opp.market_low.liquidity,
                "expires_at": opp.market_low.expires_at.isoformat() if opp.market_low.expires_at else None,
                "market_id": opp.market_low.market_id,
                "full_data": {
                    "exchange": opp.market_low.exchange,
                    "market_id": opp.market_low.market_id,
                    "question": opp.market_low.question,
                    "outcome": opp.market_low.outcome,
                    "price": opp.probability_low,
                    "volume_24h": opp.market_low.volume_24h,
                    "liquidity": opp.market_low.liquidity,
                    "expires_at": opp.market_low.expires_at.isoformat() if opp.market_low.expires_at else None,
                    "url": opp.market_low.url
                }
            },
            {
                "exchange": opp.market_high.exchange,
                "question": opp.market_high.question,
                "outcome": opp.market_high.outcome,
                "price": opp.probability_high,
                "url": opp.market_high.url,
                "liquidity": opp.market_high.liquidity,
                "expires_at": opp.market_high.expires_at.isoformat() if opp.market_high.expires_at else None,
                "market_id": opp.market_high.market_id,
                "full_data": {
                    "exchange": opp.market_high.exchange,
                    "market_id": opp.market_high.market_id,
                    "question": opp.market_high.question,
                    "outcome": opp.market_high.outcome,
                    "price": opp.probability_high,
                    "volume_24h": opp.market_high.volume_24h,
                    "liquidity": opp.market_high.liquidity,
                    "expires_at": opp.market_high.expires_at.isoformat() if opp.market_high.expires_at else None,
                    "url": opp.market_high.url
                }
            }
        ]
    }


def serialize_expert_opportunity(opp: ArbitrageOpportunityV2) -> Dict:
    """Serializa oportunidade do sistema especialista para JSON"""
    return {
        "id": opp.id,
        "type": opp.type,
        "strategy": opp.strategy,
        "profit_pct": opp.net_profit_pct,
        "gross_profit_pct": opp.gross_profit_pct,
        "total_investment": opp.total_investment,
        "expected_return": opp.expected_return,
        "risk_score": opp.risk_score,
        "confidence": opp.confidence,
        "liquidity_score": opp.liquidity_score,
        "quality_score": opp.quality_score,
        "explanation": opp.explanation,
        "execution_steps": opp.execution_steps,
        "warnings": opp.warnings,
        "detected_at": opp.detected_at.isoformat() if opp.detected_at else None,
        "markets": [
            {
                "exchange": m.exchange,
                "question": m.question,
                "outcome": m.outcome,
                "price": m.price,
                "url": m.url,
                "liquidity": m.liquidity,
                "expires_at": m.expires_at.isoformat() if m.expires_at else None,
                "market_id": m.market_id
            }
            for m in opp.markets
        ]
    }


def serialize_market(market: Market) -> Dict:
    """Serializa mercado para JSON"""
    return {
        "exchange": market.exchange,
        "market_id": market.market_id,
        "question": market.question,
        "outcome": market.outcome,
        "price": market.price,
        "volume_24h": market.volume_24h,
        "liquidity": market.liquidity,
        "expires_at": market.expires_at.isoformat() if market.expires_at else None,
        "url": market.url,
        # Inclui dados completos para permitir extração de opções específicas no frontend
        "full_data": {
            "exchange": market.exchange,
            "market_id": market.market_id,
            "question": market.question,
            "outcome": market.outcome,
            "price": market.price,
            "volume_24h": market.volume_24h,
            "liquidity": market.liquidity,
            "expires_at": market.expires_at.isoformat() if market.expires_at else None,
            "url": market.url
        }
    }


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "name": "Prediction Market Arbitrage API",
        "version": "2.0.0",
        "status": "online",
        "cache_size": len(monitor._cached_markets) if hasattr(monitor, '_cached_markets') and monitor._cached_markets else 0,
        "endpoints": {
            "/opportunities": "Lista oportunidades de arbitragem",
            "/markets": "Lista todos os mercados",
            "/stats": "Estatísticas gerais",
            "/health": "Health check rápido",
            "/paper-trading": "Estatísticas de paper trading",
            "/validate": "Valida equivalência de mercados",
            "/ws": "WebSocket para atualizações em tempo real"
        }
    }

@app.get("/health")
async def health_check():
    """Health check rápido"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "cached_markets": len(monitor._cached_markets) if hasattr(monitor, '_cached_markets') and monitor._cached_markets else 0
    }


@app.get("/opportunities")
async def get_opportunities():
    """Retorna oportunidades de arbitragem (sistema otimizado)"""
    
    # Usa cache do sistema combinatório (mais rápido)
    serialized_opportunities = []
    
    # Oportunidades tradicionais
    if hasattr(monitor, 'opportunities') and monitor.opportunities:
        for opp in monitor.opportunities:
            try:
                serialized_opportunities.append(serialize_opportunity(opp))
            except Exception as e:
                print(f"[API] Erro serializando oportunidade tradicional: {e}")
    
    # Oportunidades combinatórias
    if hasattr(monitor, 'combinatorial_opportunities') and monitor.combinatorial_opportunities:
        for opp in monitor.combinatorial_opportunities:
            try:
                serialized_opportunities.append(serialize_combinatorial_opportunity(opp))
            except Exception as e:
                print(f"[API] Erro serializando oportunidade combinatória: {e}")
    
    # Oportunidades por probabilidade (compara % entre exchanges)
    if hasattr(monitor, 'probability_opportunities') and monitor.probability_opportunities:
        for opp in monitor.probability_opportunities:
            try:
                serialized_opportunities.append(serialize_probability_opportunity(opp))
            except Exception as e:
                print(f"[API] Erro serializando oportunidade por probabilidade: {e}")
    
    # Oportunidades de curto prazo (trades rápidos/diários)
    if hasattr(monitor, 'short_term_opportunities') and monitor.short_term_opportunities:
        for opp in monitor.short_term_opportunities:
            try:
                serialized_opportunities.append(serialize_short_term_opportunity(opp))
            except Exception as e:
                print(f"[API] Erro serializando oportunidade de curto prazo: {e}")
    
    print(f"[API] GET /opportunities - Retornando {len(serialized_opportunities)} oportunidades")
    
    return {
        "opportunities": serialized_opportunities,
        "count": len(serialized_opportunities),
        "last_update": monitor.last_update.isoformat() if monitor.last_update else None,
        "system": "optimized"
    }


@app.get("/opportunities/legacy")
async def get_opportunities_legacy():
    """Retorna oportunidades do sistema antigo (compatibilidade)"""
    serialized_opportunities = []
    
    if hasattr(monitor, 'opportunities') and monitor.opportunities:
        for opp in monitor.opportunities:
            serialized_opportunities.append(serialize_opportunity(opp))
    
    if hasattr(monitor, 'combinatorial_opportunities') and monitor.combinatorial_opportunities:
        for opp in monitor.combinatorial_opportunities:
            serialized_opportunities.append(serialize_combinatorial_opportunity(opp))
    
    return {
        "opportunities": serialized_opportunities,
        "count": len(serialized_opportunities),
        "last_update": monitor.last_update.isoformat() if monitor.last_update else None,
        "system": "legacy"
    }


@app.get("/markets")
async def get_markets():
    """Retorna todos os mercados (usa cache do monitor)"""
    try:
        print(f"[API] GET /markets - Buscando mercados do cache...")
        
        # Usa o cache do monitor ao invés de buscar novamente
        # O monitor atualiza a cada 30s no background
        if not hasattr(monitor, '_cached_markets') or not monitor._cached_markets or len(monitor._cached_markets) == 0:
            print(f"[API] GET /markets - Cache vazio, buscando...")
            markets = await monitor.fetch_all_markets()
            monitor._cached_markets = markets
            print(f"[API] GET /markets - Buscado {len(markets)} mercados, cache atualizado")
        else:
            markets = monitor._cached_markets
            print(f"[API] GET /markets - Usando cache ({len(markets)} mercados)")
        
        serialized = [serialize_market(m) for m in markets]
        exchanges = list(set(m.exchange for m in markets))
        
        print(f"[API] GET /markets - Retornando {len(serialized)} mercados de {len(exchanges)} exchanges")
        
        return {
            "markets": serialized,
            "count": len(serialized),
            "exchanges": exchanges
        }
    except Exception as e:
        print(f"[API] ERRO em /markets: {e}")
        import traceback
        traceback.print_exc()
        return {
            "markets": [],
            "count": 0,
            "exchanges": [],
            "error": str(e)
        }


@app.get("/stats")
async def get_stats():
    """Retorna estatisticas gerais (usa cache)"""
    # Tenta cache
    cached = get_cached("stats", ttl=30)
    if cached:
        print(f"[API] GET /stats - Retornando cache ({cached.get('total_markets', 0)} mercados)")
        return cached
    
    print(f"[API] GET /stats - Buscando dados do cache do monitor...")
    
    # USA O CACHE DO MONITOR ao invés de buscar novamente
    if not hasattr(monitor, '_cached_markets') or not monitor._cached_markets:
        print(f"[API] GET /stats - Cache vazio, aguardando background_updates...")
        # Retorna valores vazios se cache ainda não foi populado
        return {
            "total_markets": 0,
            "total_volume_24h": 0,
            "total_liquidity": 0,
            "opportunities_count": 0,
            "by_exchange": {},
            "last_update": None,
            "paper_trading": {},
            "message": "Aguardando primeiro carregamento..."
        }
    
    markets = monitor._cached_markets
    print(f"[API] GET /stats - Usando {len(markets)} mercados do cache")
    
    # NÃO CHAMA await monitor.update() aqui - isso trava!
    # O background_updates() já faz isso a cada 30s
    
    total_volume = sum(m.volume_24h for m in markets)
    total_liquidity = sum(m.liquidity for m in markets)
    
    by_exchange = {}
    for market in markets:
        if market.exchange not in by_exchange:
            by_exchange[market.exchange] = {"count": 0, "volume": 0, "liquidity": 0}
        by_exchange[market.exchange]["count"] += 1
        by_exchange[market.exchange]["volume"] += market.volume_24h
        by_exchange[market.exchange]["liquidity"] += market.liquidity
    
    # Estatísticas de paper trading
    paper_stats = paper_trading.get_statistics()
    
    # Calcula total de oportunidades (incluindo probabilidade e curto prazo)
    total_opps = (
        (len(monitor.opportunities) if hasattr(monitor, 'opportunities') and monitor.opportunities else 0) +
        (len(monitor.combinatorial_opportunities) if hasattr(monitor, 'combinatorial_opportunities') and monitor.combinatorial_opportunities else 0) +
        (len(monitor.probability_opportunities) if hasattr(monitor, 'probability_opportunities') and monitor.probability_opportunities else 0) +
        (len(monitor.short_term_opportunities) if hasattr(monitor, 'short_term_opportunities') and monitor.short_term_opportunities else 0)
    )
    
    result = {
        "total_markets": len(markets),
        "total_volume_24h": total_volume,
        "total_liquidity": total_liquidity,
        "opportunities_count": total_opps,
        "traditional_opportunities": len(monitor.opportunities) if hasattr(monitor, 'opportunities') and monitor.opportunities else 0,
        "combinatorial_opportunities": len(monitor.combinatorial_opportunities) if hasattr(monitor, 'combinatorial_opportunities') and monitor.combinatorial_opportunities else 0,
        "probability_opportunities": len(monitor.probability_opportunities) if hasattr(monitor, 'probability_opportunities') and monitor.probability_opportunities else 0,
        "short_term_opportunities": len(monitor.short_term_opportunities) if hasattr(monitor, 'short_term_opportunities') and monitor.short_term_opportunities else 0,
        "total_matches": len(monitor.matches) if hasattr(monitor, 'matches') else 0,
        "by_exchange": by_exchange,
        "last_update": monitor.last_update.isoformat() if monitor.last_update else None,
        "paper_trading": paper_stats
    }
    set_cache("stats", result)
    return result


@app.get("/paper-trading")
async def get_paper_trading():
    """Retorna estatísticas de paper trading"""
    return paper_trading.get_statistics()


@app.post("/paper-trading/simulate")
async def simulate_trade(opportunity_index: int, amount: float = None):
    """Simula um trade de arbitragem"""
    # NÃO chama await monitor.update() - usa cache
    
    if opportunity_index >= len(monitor.opportunities):
        return {"error": "Oportunidade não encontrada"}
    
    opportunity = monitor.opportunities[opportunity_index]
    
    try:
        trade = paper_trading.simulate_trade(opportunity, amount)
        return {
            "success": True,
            "trade": {
                "amount": trade.amount,
                "profit": trade.realized_profit,
                "status": trade.status
            },
            "statistics": paper_trading.get_statistics()
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/validate")
async def validate_markets(market1_id: str, market2_id: str, exchange1: str, exchange2: str):
    """Valida equivalência entre dois mercados"""
    # USA CACHE ao invés de fetch_all_markets()
    markets = monitor._cached_markets if hasattr(monitor, '_cached_markets') and monitor._cached_markets else []
    
    market1 = next((m for m in markets if m.market_id == market1_id and m.exchange == exchange1), None)
    market2 = next((m for m in markets if m.market_id == market2_id and m.exchange == exchange2), None)
    
    if not market1 or not market2:
        return {"error": "Mercado não encontrado"}
    
    validation = validator.validate_market_pair(market1, market2)
    return validation


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para atualizações em tempo real"""
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        # Envia dados iniciais (sem atualizar, usa cache)
        await broadcast_update()
        
        # Mantém conexão viva e escuta por mensagens
        while True:
            try:
                # Aguarda mensagem do cliente (ping) ou timeout
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                # Timeout - apenas envia update (background_updates já atualiza)
                await broadcast_update()
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Erro no WebSocket: {e}")
    finally:
        if websocket in connected_clients:
            connected_clients.remove(websocket)


@app.on_event("startup")
async def startup_event():
    """Inicializa monitor ao iniciar"""
    # Inicia atualizações em background
    asyncio.create_task(background_updates())


async def background_updates():
    """Atualizações em background (OTIMIZADO - sem sistema especialista pesado)"""
    
    # Primeira atualização imediata
    print("[Background] Iniciando primeira atualização...")
    try:
        await monitor.update()
        await broadcast_update()
        print(f"[Background] OK - Primeira atualização completa")
        print(f"[Background] - Mercados: {len(monitor._cached_markets) if hasattr(monitor, '_cached_markets') else 0}")
        print(f"[Background] - Oportunidades tradicionais: {len(monitor.opportunities) if hasattr(monitor, 'opportunities') else 0}")
        print(f"[Background] - Oportunidades combinatórias: {len(monitor.combinatorial_opportunities) if hasattr(monitor, 'combinatorial_opportunities') else 0}")
    except Exception as e:
        print(f"[Background] Erro na primeira atualização: {e}")
        import traceback
        traceback.print_exc()
    
    # Loop contínuo
    from config import UPDATE_INTERVAL
    while True:
        try:
            await asyncio.sleep(UPDATE_INTERVAL)  # Usa UPDATE_INTERVAL do config
            print(f"[Background] Atualizando... (intervalo: {UPDATE_INTERVAL}s)")
            await monitor.update()
            await broadcast_update()
            total_opps = (
                (len(monitor.opportunities) if hasattr(monitor, 'opportunities') and monitor.opportunities else 0) +
                (len(monitor.combinatorial_opportunities) if hasattr(monitor, 'combinatorial_opportunities') and monitor.combinatorial_opportunities else 0) +
                (len(monitor.probability_opportunities) if hasattr(monitor, 'probability_opportunities') and monitor.probability_opportunities else 0) +
                (len(monitor.short_term_opportunities) if hasattr(monitor, 'short_term_opportunities') and monitor.short_term_opportunities else 0)
            )
            print(f"[Background] OK - Atualizado ({total_opps} oportunidades)")
        except Exception as e:
            print(f"[Background] Erro: {e}")
            await asyncio.sleep(UPDATE_INTERVAL)
