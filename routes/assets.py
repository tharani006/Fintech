"""
Assets Router for FinSight REST API
Handles asset metadata queries and custom asset additions.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from backend.database import get_db_connection
from backend.schemas import AssetSchema, AssetCreateSchema

router = APIRouter(prefix="/api/assets", tags=["Assets"])

@router.get("", response_model=List[AssetSchema])
def get_all_assets():
    """Retrieves list of all available multi-asset instruments."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, symbol, color, initial_price, volatility, trend FROM assets")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.get("/{asset_id}", response_model=AssetSchema)
def get_asset_by_id(asset_id: str):
    """Retrieves specific asset metadata by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, symbol, color, initial_price, volatility, trend FROM assets WHERE id = ?", (asset_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail=f"Asset with ID '{asset_id}' not found.")
    return dict(row)

@router.post("", response_model=AssetSchema, status_code=201)
def create_custom_asset(asset: AssetCreateSchema):
    """Registers a new custom financial asset instrument in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO assets (id, name, category, symbol, color, initial_price, volatility, trend)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (asset.id, asset.name, asset.category, asset.symbol, asset.color, asset.initial_price, asset.volatility, asset.trend))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Asset ID '{asset.id}' already exists or invalid data.")
    conn.close()
    return asset.dict()
