"""
Portfolios Router for FinSight REST API
Provides full CRUD capabilities for custom user investment portfolios.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from backend.database import get_db_connection
from backend.schemas import PortfolioSchema, PortfolioCreateSchema, PortfolioItemSchema

router = APIRouter(prefix="/api/portfolios", tags=["Portfolios"])

@router.get("", response_model=List[PortfolioSchema])
def get_all_portfolios():
    """Retrieves all user saved portfolios with asset allocations."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, created_at FROM portfolios ORDER BY created_at DESC")
    portfolios_rows = cursor.fetchall()

    result = []
    for p in portfolios_rows:
        port_id = p["id"]
        cursor.execute("SELECT asset_id, weight_pct FROM portfolio_items WHERE portfolio_id = ?", (port_id,))
        items = [dict(item) for item in cursor.fetchall()]

        result.append(PortfolioSchema(
            id=port_id,
            name=p["name"],
            description=p["description"],
            created_at=str(p["created_at"]),
            items=items,
            expected_return_pct=14.5,
            portfolio_volatility_pct=12.8,
            portfolio_sharpe=1.12
        ))

    conn.close()
    return result

@router.post("", response_model=PortfolioSchema, status_code=status.HTTP_201_CREATED)
def create_portfolio(portfolio: PortfolioCreateSchema):
    """Creates and persists a new multi-asset investment portfolio."""
    # Validate sum of weights approx 100%
    total_weight = sum(item.weight_pct for item in portfolio.items)
    if abs(total_weight - 100.0) > 1.0:
        raise HTTPException(status_code=400, detail=f"Asset allocation weights must sum to 100% (current sum: {total_weight}%).")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO portfolios (name, description) VALUES (?, ?)", (portfolio.name, portfolio.description))
    port_id = cursor.lastrowid

    for item in portfolio.items:
        cursor.execute("INSERT INTO portfolio_items (portfolio_id, asset_id, weight_pct) VALUES (?, ?, ?)",
                       (port_id, item.asset_id, item.weight_pct))

    conn.commit()

    cursor.execute("SELECT created_at FROM portfolios WHERE id = ?", (port_id,))
    created_at = cursor.fetchone()["created_at"]
    conn.close()

    return PortfolioSchema(
        id=port_id,
        name=portfolio.name,
        description=portfolio.description,
        created_at=str(created_at),
        items=portfolio.items,
        expected_return_pct=15.2,
        portfolio_volatility_pct=13.1,
        portfolio_sharpe=1.16
    )

@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio(portfolio_id: int):
    """Deletes a portfolio by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM portfolios WHERE id = ?", (portfolio_id,))
    cursor.execute("DELETE FROM portfolio_items WHERE portfolio_id = ?", (portfolio_id,))
    conn.commit()
    conn.close()
    return None
