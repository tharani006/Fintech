"""
Pydantic Schemas for FinSight REST API request validation and response serialization.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class AssetSchema(BaseModel):
    id: str
    name: str
    category: str
    symbol: str
    color: str
    initial_price: float
    volatility: float
    trend: float

class AssetCreateSchema(BaseModel):
    id: str
    name: str
    category: str
    symbol: str
    color: str
    initial_price: float
    volatility: float = 0.02
    trend: float = 0.0005

class PricePointSchema(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class QuantMetricsSchema(BaseModel):
    asset_id: str
    asset_name: str
    initial_price: float
    latest_price: float
    cagr_pct: float
    annual_volatility_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown_pct: float
    var_95_pct: float
    win_rate_pct: float
    total_days: int

class BacktestRequestSchema(BaseModel):
    asset_id: str = "btc"
    strategy_id: str = "sma_cross"  # "sma_cross", "rsi_reversion", "momentum", "buy_hold"
    initial_capital: float = 10000.0
    position_size_pct: float = 100.0
    transaction_fee_pct: float = 0.1
    sma_fast: int = 50
    sma_slow: int = 200
    rsi_period: int = 14
    rsi_oversold: float = 30.0
    rsi_overbought: float = 70.0

class TradeLogSchema(BaseModel):
    type: str  # "BUY" or "SELL"
    date: str
    price: float
    shares: float
    capital_after: float
    fee: float

class BacktestResultSchema(BaseModel):
    asset_id: str
    strategy_id: str
    initial_capital: float
    final_capital: float
    total_return_pct: float
    buy_hold_return_pct: float
    alpha_pct: float
    sharpe_ratio: float
    max_drawdown_pct: float
    total_trades: int
    winning_trades: int
    win_rate_pct: float
    trade_history: List[TradeLogSchema]
    equity_curve: List[Dict[str, Any]]

class TimeMachineRequestSchema(BaseModel):
    asset_id: str = "btc"
    start_date: str = "2020-01-01"
    initial_capital: float = 10000.0
    monthly_sip: float = 0.0

class TimeMachineResultSchema(BaseModel):
    asset_id: str
    asset_name: str
    start_date: str
    initial_capital: float
    total_invested: float
    final_value: float
    profit_loss: float
    return_pct: float
    cagr_pct: float
    peak_value: float
    multiplier: float

class RegimeAnalysisRequestSchema(BaseModel):
    asset_id: str = "btc"
    lookback_days: int = 252

class RegimeResultSchema(BaseModel):
    asset_id: str
    current_regime: str
    regime_confidence_pct: float
    regime_breakdown: Dict[str, float]
    transition_matrix: Dict[str, Dict[str, float]]
    historical_regimes: List[Dict[str, Any]]

class PortfolioItemSchema(BaseModel):
    asset_id: str
    weight_pct: float

class PortfolioCreateSchema(BaseModel):
    name: str
    description: Optional[str] = ""
    items: List[PortfolioItemSchema]

class PortfolioSchema(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: str
    items: List[PortfolioItemSchema]
    expected_return_pct: Optional[float] = 0.0
    portfolio_volatility_pct: Optional[float] = 0.0
    portfolio_sharpe: Optional[float] = 0.0
