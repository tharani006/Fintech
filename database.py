"""
FinSight SQLite Database Interface & Initialization Module
Manages database schema, connection pooling, and historical price seeding.
"""

import sqlite3
import os
import math
from typing import Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "fintech.db")

def get_db_connection():
    """Establishes and returns a SQLite connection with row dictionary access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Creates initial database tables and seeds sample assets & historical data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Asset Metadata Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        symbol TEXT NOT NULL,
        color TEXT NOT NULL,
        initial_price REAL NOT NULL,
        volatility REAL NOT NULL,
        trend REAL NOT NULL
    );
    """)

    # Daily Price History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id TEXT NOT NULL,
        date TEXT NOT NULL,
        open REAL NOT NULL,
        high REAL NOT NULL,
        low REAL NOT NULL,
        close REAL NOT NULL,
        volume INTEGER NOT NULL,
        FOREIGN KEY (asset_id) REFERENCES assets (id),
        UNIQUE(asset_id, date)
    );
    """)

    # User Portfolios Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Portfolio Assets Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        portfolio_id INTEGER NOT NULL,
        asset_id TEXT NOT NULL,
        weight_pct REAL NOT NULL,
        FOREIGN KEY (portfolio_id) REFERENCES portfolios (id) ON DELETE CASCADE,
        FOREIGN KEY (asset_id) REFERENCES assets (id)
    );
    """)

    # Backtest Execution History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS backtest_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id TEXT NOT NULL,
        strategy_id TEXT NOT NULL,
        initial_capital REAL NOT NULL,
        final_capital REAL NOT NULL,
        total_return_pct REAL NOT NULL,
        sharpe_ratio REAL NOT NULL,
        max_drawdown_pct REAL NOT NULL,
        trade_count INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()

    # Seed Initial Assets if Empty
    cursor.execute("SELECT COUNT(*) FROM assets")
    if cursor.fetchone()[0] == 0:
        seed_assets_and_prices(cursor)
        conn.commit()

    conn.close()

def seeded_random(seed: float) -> float:
    """Deterministic pseudo-random generator matching JS implementation."""
    x = math.sin(seed) * 10000
    return x - math.floor(x)

def seed_assets_and_prices(cursor):
    """Populates database with 6 financial assets and 5-year daily OHLCV dataset."""
    assets_data = [
        {"id": "gold", "name": "Gold (XAU/USD)", "category": "Commodity", "symbol": "XAU", "color": "#F59E0B", "initial_price": 1520.0, "volatility": 0.011, "trend": 0.00035},
        {"id": "btc", "name": "Bitcoin (BTC/USD)", "category": "Cryptocurrency", "symbol": "BTC", "color": "#F7931A", "initial_price": 7200.0, "volatility": 0.038, "trend": 0.0011},
        {"id": "nvda", "name": "NVIDIA Corp", "category": "Technology / AI", "symbol": "NVDA", "color": "#10B981", "initial_price": 60.0, "volatility": 0.028, "trend": 0.0018},
        {"id": "aapl", "name": "Apple Inc", "category": "Technology", "symbol": "AAPL", "color": "#3B82F6", "initial_price": 75.0, "volatility": 0.018, "trend": 0.0008},
        {"id": "spy", "name": "S&P 500 Index ETF", "category": "Index / Equities", "symbol": "SPY", "color": "#6366F1", "initial_price": 320.0, "volatility": 0.012, "trend": 0.0005},
        {"id": "eth", "name": "Ethereum (ETH/USD)", "category": "Cryptocurrency", "symbol": "ETH", "color": "#8B5CF6", "initial_price": 130.0, "volatility": 0.042, "trend": 0.0013}
    ]

    for asset in assets_data:
        cursor.execute("""
        INSERT INTO assets (id, name, category, symbol, color, initial_price, volatility, trend)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (asset["id"], asset["name"], asset["category"], asset["symbol"], asset["color"],
              asset["initial_price"], asset["volatility"], asset["trend"]))

        # Generate ~1,260 days of historical prices
        seed = sum(ord(c) for c in asset["id"])
        current_price = asset["initial_price"]

        for i in range(1260):
            # Calculate date from 2020-01-01
            year_offset = i // 365
            day_of_year = i % 365
            # Simplified daily generator
            date_str = f"{2020 + year_offset}-{1 + (day_of_year // 30):02d}-{1 + (day_of_year % 28):02d}"

            cycle_factor = 0.0
            if 50 <= i <= 85:
                cycle_factor = -0.015  # COVID Crash
            elif 85 < i <= 450:
                cycle_factor = 0.0025 if "crypto" in asset["category"].lower() else 0.001
            elif 450 < i <= 750:
                cycle_factor = -0.002 if "crypto" in asset["category"].lower() else -0.0008
            elif i > 750:
                cycle_factor = 0.003 if asset["id"] in ["nvda", "btc"] else 0.0008

            rand1 = max(0.0001, seeded_random(seed))
            seed += 1
            rand2 = seeded_random(seed)
            seed += 1

            norm_rand = math.sqrt(-2.0 * math.log(rand1)) * math.cos(2.0 * math.pi * rand2)
            daily_return = asset["trend"] + cycle_factor + (asset["volatility"] * norm_rand)

            open_p = current_price
            current_price = max(open_p * 0.1, open_p * (1.0 + daily_return))
            close_p = current_price

            spread = abs(norm_rand) * asset["volatility"] * open_p * 1.2
            high_p = max(open_p, close_p) + spread * 0.6
            low_p = min(open_p, close_p) - spread * 0.4
            vol = int(1000000 * (0.7 + seeded_random(seed) * 0.6))
            seed += 1

            cursor.execute("""
            INSERT OR IGNORE INTO price_history (asset_id, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (asset["id"], date_str, round(open_p, 2), round(high_p, 2), round(low_p, 2), round(close_p, 2), vol))

    # Seed Default Portfolios
    cursor.execute("INSERT INTO portfolios (name, description) VALUES (?, ?)", 
                   ("Tech & Crypto Alpha", "Aggressive growth portfolio combining AI tech and major cryptocurrencies"))
    port_id = cursor.lastrowid
    cursor.execute("INSERT INTO portfolio_items (portfolio_id, asset_id, weight_pct) VALUES (?, ?, ?)", (port_id, "nvda", 40.0))
    cursor.execute("INSERT INTO portfolio_items (portfolio_id, asset_id, weight_pct) VALUES (?, ?, ?)", (port_id, "btc", 35.0))
    cursor.execute("INSERT INTO portfolio_items (portfolio_id, asset_id, weight_pct) VALUES (?, ?, ?)", (port_id, "eth", 25.0))

    cursor.execute("INSERT INTO portfolios (name, description) VALUES (?, ?)", 
                   ("Balanced Macro Shield", "Defensive multi-asset portfolio with gold, S&P 500, and tech"))
    port_id2 = cursor.lastrowid
    cursor.execute("INSERT INTO portfolio_items (portfolio_id, asset_id, weight_pct) VALUES (?, ?, ?)", (port_id2, "gold", 40.0))
    cursor.execute("INSERT INTO portfolio_items (portfolio_id, asset_id, weight_pct) VALUES (?, ?, ?)", (port_id2, "spy", 40.0))
    cursor.execute("INSERT INTO portfolio_items (portfolio_id, asset_id, weight_pct) VALUES (?, ?, ?)", (port_id2, "aapl", 20.0))
