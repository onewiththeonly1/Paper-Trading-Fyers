# Paper Trading Application - Fyers Edition

**Ultra-Low Latency | Single-Keystroke Trading | Paper Trading Mode | Web Dashboard | Python-Based**

---

## Table of Contents

1. What This Application Offers
2. Project Structure
3. API Credentials & Configuration
4. Important URLs
5. Dependencies
6. Setup & Installation
7. Fyers API Setup
8. Running the Application
9. Trading Commands
10. Web Dashboard
11. Paper Trading Features
12. Trade History & Analytics
13. Change Instrument During Trading
14. Best Practices
15. Testing Guide
16. Common Issues & Solutions
17. Technical Artifacts
18. Important Notes

---

## 1. What This Application Offers

### Dual Trading Modes

- **PAPER TRADING** - Simulated trading with no real money at risk
- **REAL TRADING** - Live order execution with actual capital
- Switch between modes at startup with confirmation

### Instant Single-Keystroke Trading

- No `Enter` key — every action is **immediate**
- Buy, sell, close, change instruments, quit — all with **single keys**
- Raw terminal input for zero latency

### Instant Instrument Selection

- Select instruments using **1–9, A–Z**
- Supports **up to 35 instruments**
- Case-insensitive (`a` = `A`)
- Press `Q` anytime to exit

### Silent Console, Full Visibility

- Console goes silent after selection
- **Everything logged** to `trading.log`
- Real-time **log viewer in Web UI**

### Paper Trading Features

- **Realistic Execution** - Uses best bid/ask prices from market depth
- **Trade Ledger** - Complete history of all round-trip trades
- **Session Statistics** - Net P&L, win rate, total trades, and more
- **CSV Export** - Export all trades for analysis
- **FIFO Matching** - Accurate P&L calculation for partial exits

### Fyers API - Free Tier Compatible

- Position tracking via **executed order prices**
- Fully usable for **real trading**
- No WebSocket required for basic functionality

### Optimized for Options & Equities

- NIFTY / BANKNIFTY / Equity supported
- INTRADAY / MARGIN / CNC products

---

## 2. Project Structure

```
paper-trading-fyers/
├── main.py                 # Main application entry point
├── generate_token.py       # Token generation script
├── config.json             # Configuration (credentials, instruments)
├── requirements.txt        # Python dependencies
├── trading.log            # Application logs
├── verify.py             # Verification script
├── internal/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── logger.py          # Logging system
│   ├── position.py        # Position & trade management
│   ├── trader.py          # Order execution (Trader & PaperTrader)
│   ├── terminal.py        # Raw terminal input handling
│   └── server.py          # Flask web server
├── web/
│   └── index.html         # Web dashboard UI
└── trades/
    └── paper_trades_*.csv # Exported trade history
```

---

## 3. API Credentials & Configuration

### Configuration Fields (config.json)

| Field | Description |
|-------|-------------|
| `app_id` | Fyers API Application ID |
| `app_secret` | Fyers API Application Secret |
| `redirect_uri` | OAuth Redirect URI |
| `access_token` | Access token (expires daily at 6:00 AM IST) |
| `instruments` | List of trading instruments |

### Example config.json

```json
{
  "app_id": "YOUR_APP_ID",
  "app_secret": "YOUR_APP_SECRET",
  "redirect_uri": "https://trade.fyers.in/api-login/redirect-uri/index.html",
  "access_token": "YOUR_ACCESS_TOKEN",
  "instruments": [
    {
      "symbol": "NSE:NIFTY26JAN25000CE",
      "exchange": "NSE",
      "lot_size": 65,
      "product": "MARGIN"
    },
    {
      "symbol": "NSE:BANKNIFTY26JAN58700CE",
      "exchange": "NSE",
      "lot_size": 30,
      "product": "INTRADAY"
    },
    {
      "symbol": "NSE:SBIN-EQ",
      "exchange": "NSE",
      "lot_size": 1,
      "product": "CNC"
    }
  ]
}
```

### Configured Trading Instruments

| # | Symbol | Exchange | Lot Size | Product |
|---|--------|----------|----------|---------|
| 1 | `NSE:NIFTY26FEB25000CE` | NSE | 65 | MARGIN |
| 2 | `NSE:NIFTY2620325200CE` | NSE | 65 | MARGIN |
| 3 | `NSE:NIFTY26FEB25500PE` | NSE | 65 | MARGIN |
| 4 | `NSE:NIFTY2620325400CE` | NSE | 65 | MARGIN |
| 5 | `NSE:NIFTY2620325500PE` | NSE | 65 | MARGIN |
| 6 | `NSE:SBIN-EQ` | NSE | 1 | CNC |

### Product Types

| Product | Description |
|---------|-------------|
| `CNC` | For equity only (Cash & Carry) |
| `INTRADAY` | Applicable for all segments |
| `MARGIN` | Applicable only for derivatives |
| `CO` | Cover Order |
| `BO` | Bracket Order |
| `MTF` | Margin Trading Facility |

---

## 4. Important URLs

### Fyers API & Developer Portal

| URL | Purpose |
|-----|---------|
| `https://myapi.fyers.in/dashboard/` | Fyers API Developer Dashboard |
| `https://myapi.fyers.in/docsv3` | API Documentation |
| `https://trade.fyers.in/api-login/redirect-uri/index.html` | Redirect URI |

### Symbol Master Files

| URL | Exchange/Segment |
|-----|------------------|
| `https://public.fyers.in/sym_details/NSE_FO.csv` | NSE - Equity Derivatives |
| `https://public.fyers.in/sym_details/NSE_CM.csv` | NSE - Capital Market |
| `https://public.fyers.in/sym_details/BSE_CM.csv` | BSE - Capital Market |

### Local Application URLs

| URL | Description |
|-----|-------------|
| `http://localhost:8080` | Web Dashboard |

---

## 5. Dependencies

```
fyers-apiv3==3.1.8
flask==3.0.0
flask-cors==4.0.0
```

---

## 6. Setup & Installation

### Prerequisites

1. **Python 3.8 or higher**
2. **Linux/Mac** (for terminal raw mode support)
3. **Fyers Trading Account** with API access

### Step-by-Step Setup

```bash
# Navigate to project directory
cd ~/paper-trading-fyers

# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 7. Fyers API Setup

### Create Fyers App

1. Visit https://myapi.fyers.in/dashboard/
2. Click "Create App" → "Personal App"
3. Fill in details:
   - App Name: "Paper Trading App"
   - Redirect URI: `https://trade.fyers.in/api-login/redirect-uri/index.html`
4. Note your `app_id` and `app_secret`

### Generate Access Token

```bash
python generate_token.py
```

**Important:** Tokens expire at 6:00 AM IST daily.

---

## 8. Running the Application

### Start the Application

```bash
python main.py
```

### Trading Mode Selection

```
1. Paper Trading (Simulated)
2. Real Trading (Live market)

Select mode (1 or 2):
```

- Press `1` for Paper Trading (recommended)
- Press `2` for Real Trading (requires "yes" confirmation)

### Instrument Selection

Press keys 1-9 or A-Z to select instrument

---

## 9. Trading Commands (No Enter Ever)

| Key | Action |
|-----|--------|
| `1`–`9` | Buy lots |
| `-1`–`-9` | Sell lots |
| `--` | Close all positions |
| `C` | Change instrument (when flat) |
| `Q` | Quit app |

---

## 10. Web Dashboard

### Access

```
http://localhost:8080
```

### Features

- Real-time Position Panel
- Live MTM P&L
- Order History
- Activity Logs
- Session Statistics (Paper mode)
- Trade Ledger (Paper mode)
- CSV Export (Paper mode)

---

## 11. Paper Trading Features

### Execution Logic

**BUY Orders:**
- Fetches market depth
- Uses best ASK price
- Updates position

**SELL Orders:**
- Fetches market depth
- Uses best BID price
- Matches with pending buys (FIFO)
- Creates trade record with P&L

---

## 12. Trade History & Analytics

### Session Statistics

- Net P&L
- Total Trades
- Win Rate
- Winning/Losing Trades
- Total Turnover

### CSV Export

- Click "Export CSV" in dashboard
- Saved to `trades/paper_trades_YYYYMMDD_HHMMSS.csv`
- Auto-export on app exit

---

## 13. Change Instrument During Trading

Press `C` (only when no open positions):

```
=== Available Instruments ===
1. NSE:NIFTY26JAN25100CE [MARGIN]
Select instrument: 2
```

---

## 14. Best Practices

### Daily Routine
1. Generate token (8:30 AM) - `python generate_token.py`
2. Update weekly expiry symbols in `config.json`
3. Start app - `python main.py`
4. Select Paper/Real mode
5. Monitor dashboard at http://localhost:8080

### Instrument Organization
- 1–3 → Intraday options
- 4–6 → Positional
- 7–9 → Equity

---

## 15. Testing Guide

### Test 1: Paper Trading Mode

1. Start: `python main.py`
2. Select: `1` (Paper Trading)
3. Select Instrument: `1`
4. Buy: `2` (2 lots)
5. Sell: `-3` (3 lots)
6. View Dashboard

### Test 2: Verify No Real Orders

1. Start in paper mode
2. Place trades
3. Check Fyers account - **no orders should appear**

### Test 3: Real Trading (Caution!)

```bash
python main.py
Select mode: 2
Confirm: yes
```

⚠️ Uses real money!

---

## 16. Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | Activate virtual environment |
| Terminal not responding | Run from system terminal |
| Token Expired | Run `python generate_token.py` |
| Dashboard Not Loading | Check port 8080 |
| Trades Not Exporting | `mkdir -p trades` |

---

## 17. Technical Artifacts

### Runtime Commands

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Daily token
python generate_token.py

# Run
python main.py

# Logs
tail -f trading.log
grep ERROR trading.log
grep "[PAPER]" trading.log
```

### Performance

| Operation | Time |
|-----------|------|
| Order (paper) | < 200ms |
| Order (real) | < 500ms |
| Dashboard refresh | 500ms |

---

## 18. Important Notes

### Token Validity
- Expires at **6:00 AM IST daily**
- Generate new token each trading day

### Terminal Requirements
- Run from proper terminal, not IDE console

### Safety Warnings

**Paper Trading:** ✅ Zero risk
**Real Trading:** ⚠️ Actual capital at risk

### Symbol Updates
- Update weekly expiry symbols every Thursday

---

## Example Usage Flow

### Paper Trading
```
1. python main.py
2. Select: 1 (Paper)
3. Select Instrument: 1
4. Buy: 2
5. Sell: -3
6. Export: Click CSV
7. Quit: Q
```

### Real Trading
```
1. python main.py
2. Select: 2 (Real)
3. Confirm: yes
4. Buy: 1
5. Sell: -1
```

---

## Key Differences

| Feature | Original | Paper App |
|---------|----------|-----------|
| Modes | Real only | Paper + Real |
| Trade History | Orders only | Full ledger |
| P&L Tracking | MTM | MTM + Realized |
| Export | None | CSV |

---

## Daily Workflow

### Morning (Before Market)
1. Generate token
2. Update instruments
3. Start application

### End of Day
1. Close all positions
2. Export trades (auto on exit)
3. Press Q to quit

---

## Support

- **Fyers API Docs**: https://myapi.fyers.in/docsv3
- **Symbol Master**: https://public.fyers.in/sym_details/

---

## License

Trading utility application. Use at your own risk.

---

## Conclusion

A **professional-grade paper trading application**:
- ✅ Paper + Real trading modes
- ✅ Detailed trade analytics
- ✅ Risk-free strategy testing
- ✅ Seamless transition to real trading

**Ready to use after setup!**

**Happy Paper Trading! 🚀📈**
