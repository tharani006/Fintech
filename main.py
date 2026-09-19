"""
FinSight Python FastAPI Application Main Entry Point
Configures API routing, CORS policy, database lifecycle, and OpenAPI specs.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.database import init_db
from backend.routes import assets, prices, quant, portfolios

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup & shutdown events."""
    print("[INIT] Initializing FinSight SQLite Database & Seeding Historical Price Datasets...")
    init_db()
    print("[INIT] Database ready. Starting FinSight FastAPI Server.")
    yield
    print("[SHUTDOWN] Shutting down FinSight FastAPI Server.")

app = FastAPI(
    title="FinSight Quantitative Intelligence API",
    description="High-performance REST API for multi-asset quantitative research, risk metrics, strategy backtesting, and portfolio analytics.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable Cross-Origin Resource Sharing (CORS) for seamless frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Route Routers
app.include_router(assets.router)
app.include_router(prices.router)
app.include_router(quant.router)
app.include_router(portfolios.router)

@app.get("/api/health", tags=["System"])
def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": "FinSight Quantitative FastAPI Backend",
        "version": "1.0.0",
        "database": "SQLite (fintech.db)"
    }

@app.get("/api/explainer/{topic}", tags=["Explainer"])
def get_quantitative_explainer(topic: str):
    """Returns AI quantitative explanation for financial concepts."""
    explainers = {
        "sharpe": {
            "title": "Sharpe Ratio Explained",
            "explanation": "The Sharpe Ratio measures the excess return per unit of total risk (volatility). A higher ratio indicates superior risk-adjusted performance.",
            "takeaway": "Aim for strategies with a Sharpe Ratio > 1.0; values > 2.0 indicate exceptional risk efficiency."
        },
        "drawdown": {
            "title": "Maximum Drawdown Explained",
            "explanation": "Maximum Drawdown represents the peak-to-trough decline during a specific period. It measures tail-risk equity loss.",
            "takeaway": "Risk management rules (e.g. stop-loss or diversification) limit maximum drawdown during market crashes."
        },
        "regime": {
            "title": "Market Regime Shifts Explained",
            "explanation": "Financial markets alternate between structural regimes like low-volatility bull runs and high-volatility liquidity shocks.",
            "takeaway": "Dynamic position sizing based on regime detection protects capital during crisis transitions."
        }
    }
    
    key = topic.lower()
    if key in explainers:
        return explainers[key]
    
    return {
        "title": f"Quantitative Insight: {topic.capitalize()}",
        "explanation": f"Quantitative analysis relies on statistical models to evaluate asset behavior, correlations, and risk exposure.",
        "takeaway": "Always combine quantitative signals with strict portfolio risk management."
    }
