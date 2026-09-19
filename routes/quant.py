"""
Quantitative Analytics Router for FinSight REST API
Executes risk metrics, strategy backtests, time machine investments, and market regime analysis.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from backend.database import get_db_connection
from backend.schemas import (
    QuantMetricsSchema, BacktestRequestSchema, BacktestResultSchema,
    TimeMachineRequestSchema, TimeMachineResultSchema, RegimeAnalysisRequestSchema, RegimeResultSchema
)
from backend.quant_services import (
    calculate_quant_metrics, run_backtest_strategy, calculate_time_machine, analyze_market_regimes
)

router = APIRouter(prefix="/api/quant", tags=["Quantitative Analytics"])

def _fetch_prices_for_asset(asset_id: str) -> List[Dict[str, Any]]:
    """Helper to query price history for a given asset ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT date, open, high, low, close, volume FROM price_history WHERE asset_id = ? ORDER BY date ASC", (asset_id,))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail=f"No price data available for asset '{asset_id}'.")
    return [dict(row) for row in rows]

def _fetch_asset_name(asset_id: str) -> str:
    """Helper to get asset name."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM assets WHERE id = ?", (asset_id,))
    row = cursor.fetchone()
    conn.close()
    return row["name"] if row else asset_id

@router.get("/metrics/{asset_id}", response_model=QuantMetricsSchema)
def get_asset_quant_metrics(asset_id: str):
    """Computes server-side quantitative risk and return metrics for an asset."""
    prices = _fetch_prices_for_asset(asset_id)
    asset_name = _fetch_asset_name(asset_id)
    return calculate_quant_metrics(asset_id, asset_name, prices)

@router.post("/backtest", response_model=BacktestResultSchema)
def execute_backtest(req: BacktestRequestSchema):
    """Executes server-side algorithmic strategy backtest and logs run to database."""
    prices = _fetch_prices_for_asset(req.asset_id)
    result = run_backtest_strategy(req, prices)

    # Persist backtest run to database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO backtest_runs (asset_id, strategy_id, initial_capital, final_capital, total_return_pct, sharpe_ratio, max_drawdown_pct, trade_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (req.asset_id, req.strategy_id, req.initial_capital, result.final_capital, result.total_return_pct, result.sharpe_ratio, result.max_drawdown_pct, result.total_trades))
        conn.commit()
        conn.close()
    except Exception as e:
        pass  # Non-blocking log write

    return result

@router.post("/timemachine", response_model=TimeMachineResultSchema)
def run_time_machine_simulation(req: TimeMachineRequestSchema):
    """Simulates historical lump-sum or DCA investment strategy."""
    prices = _fetch_prices_for_asset(req.asset_id)
    asset_name = _fetch_asset_name(req.asset_id)
    return calculate_time_machine(req, asset_name, prices)

@router.get("/regime/{asset_id}", response_model=RegimeResultSchema)
def get_market_regimes(asset_id: str):
    """Analyzes market volatility regimes and Markov transition probability matrix."""
    prices = _fetch_prices_for_asset(asset_id)
    return analyze_market_regimes(prices)
