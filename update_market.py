#!/usr/bin/env python3
"""
update_market.py — Fetch latest market closes and write data/market.json

Usage:
    pip install yfinance
    python update_market.py

Tickers configured:
    S&P 500     ^GSPC
    BVL IGBVL   S&P/BVL General (via ^SPBLPGPT or manual fallback)
    USD/PEN     PEN=X
    EUR/PEN     EURPEN=X

The script fetches the last 5 trading days, computes close-to-close change,
and writes a JSON file that the frontend reads automatically.

To automate: schedule with cron (Linux/Mac) or Task Scheduler (Windows).
  Example cron (runs every weekday at 6pm Lima time):
    0 18 * * 1-5 cd /path/to/rp-news && python update_market.py
"""

import json
import os
import sys
from datetime import datetime

try:
    import yfinance as yf
except ImportError:
    print("Error: yfinance not installed. Run: pip install yfinance")
    sys.exit(1)

# ════════════════════════════════════════════
# CONFIGURE YOUR TICKERS HERE
# label     : display name in the market bar
# symbol    : Yahoo Finance ticker symbol
# decimals  : how many decimals to show for the value
# ════════════════════════════════════════════
TICKERS = [
    {"label": "S&P 500",   "symbol": "^GSPC",      "decimals": 2},
    {"label": "BVL IGBVL", "symbol": "^SPBLPGPT",  "decimals": 2},
    {"label": "USD/PEN",   "symbol": "PEN=X",      "decimals": 4},
    {"label": "EUR/PEN",   "symbol": "EURPEN=X",   "decimals": 4},
]


def fetch_indicator(label, symbol, decimals):
    """Fetch latest close and previous close, compute change."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d")

        if hist.empty or len(hist) < 1:
            print(f"  ⚠ {label} ({symbol}): no data returned")
            return None

        last_close = float(hist["Close"].iloc[-1])

        if len(hist) >= 2:
            prev_close = float(hist["Close"].iloc[-2])
            change = last_close - prev_close
            pct = (change / prev_close) * 100
        else:
            change = 0.0
            pct = 0.0

        direction = "up" if change >= 0 else "down"

        fmt_val = f"{last_close:,.{decimals}f}"
        fmt_chg = f"{change:+.{decimals}f}"
        fmt_pct = f"{pct:+.2f}%"

        last_date = hist.index[-1].strftime("%d %b %Y")

        print(f"  ✓ {label}: {fmt_val}  {fmt_chg}  {fmt_pct}  ({last_date})")

        return {
            "label": label,
            "value": fmt_val,
            "change": fmt_chg,
            "pct": fmt_pct,
            "direction": direction,
            "date": last_date,
        }

    except Exception as e:
        print(f"  ✗ {label} ({symbol}): {e}")
        return None


def main():
    print(f"Fetching market data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")

    indicators = []
    latest_date = ""

    for t in TICKERS:
        result = fetch_indicator(t["label"], t["symbol"], t["decimals"])
        if result:
            indicators.append(result)
            latest_date = result["date"]  # use last successful date
        else:
            # Fallback: show dashes for failed tickers
            indicators.append({
                "label": t["label"],
                "value": "---",
                "change": "---",
                "pct": "---",
                "direction": "neutral",
                "date": "",
            })

    output = {
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated": f"Cierre {latest_date}" if latest_date else "Sin datos",
        "indicators": indicators,
    }

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "market.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Wrote {out_path}")
    print(f"  {len([i for i in indicators if i['value'] != '---'])}/{len(TICKERS)} indicators loaded")


if __name__ == "__main__":
    main()
