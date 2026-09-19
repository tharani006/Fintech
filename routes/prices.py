"""
Price History Router for FinSight REST API
Provides historical daily OHLCV candlestick data series.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from backend.database import get_db_connection
from backend.schemas import PricePointSchema

router = APIRouter(prefix="/api/prices", tags=["Prices"])

@router.get("/{asset_id}", response_model=List[PricePointSchema])
def get_asset_prices(
    asset_id: str,
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD")
):
    """Retrieves historical OHLCV price series for an asset with optional date filtering."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT date, open, high, low, close, volume FROM price_history WHERE asset_id = ?"
    params = [asset_id]

    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)

    query += " ORDER BY date ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No price history found for asset '{asset_id}'.")

    return [dict(row) for row in rows]
