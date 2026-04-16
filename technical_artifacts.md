# Technical Artifacts - Paper Trading Fyers Application

This document captures all important URLs, credentials, settings, and runtime instructions for the Paper Trading Fyers application.

---

## 1. API Credentials & Configuration

### Current Configuration (config.json)

| Field | Value | Description |
|-------|-------|-------------|
| `app_id` | `9ZH3K009J7-100` | Fyers API Application ID |
| `app_secret` | `RPYJRYS1XG` | Fyers API Application Secret |
| `redirect_uri` | `https://trade.fyers.in/api-login/redirect-uri/index.html` | OAuth Redirect URI |
| `access_token` | (JWT token) | Access token (expires daily at 6:00 AM IST) |

### Configured Trading Instruments

| # | Symbol | Exchange | Lot Size | Product |
|---|--------|----------|----------|---------|
| 1 | `NSE:NIFTY26FEB25000CE` | NSE | 65 | MARGIN |
| 2 | `NSE:NIFTY2620325200CE` | NSE | 65 | MARGIN |
| 3 | `NSE:NIFTY26FEB25500PE` | NSE | 65 | MARGIN |
| 4 | `NSE:NIFTY2620325400CE` | NSE | 65 | MARGIN |
| 5 | `NSE:NIFTY2620325500PE` | NSE | 65 | MARGIN |
| 6 | `NSE:SBIN-EQ` | NSE | 1 | CNC |

---

## 2. Important URLs

### Fyers API & Developer Portal

| URL | Purpose |
|-----|---------|
| `https://myapi.fyers.in/dashboard/` | Fyers API Developer Dashboard |
| `https://myapi.fyers.in/docsv3` | API Documentation |
| `https://trade.fyers.in/api-login/redirect-uri/index.html` | Redirect URI (used in OAuth) |

### Symbol Master Files (for getting trading symbols)

| URL | Exchange/Segment |
|-----|------------------|
| `https://public.fyers.in/sym_details/NSE_CD.csv` | NSE - Currency Derivatives |
| `https://public.fyers.in/sym_details/NSE_FO.csv` | NSE - Equity Derivatives |
| `https://public.fyers.in/sym_details/NSE_COM.csv` | NSE - Commodity |
| `https://public.fyers.in/sym_details/NSE_CM.csv` | NSE - Capital Market |
| `https://public.fyers.in/sym_details/BSE_CM.csv` | BSE - Capital Market |
| `https://public.fyers.in/sym_details/BSE_FO.csv` | BSE - Equity Derivatives |
| `https://public.fyers.in/sym_details/MCX_COM.csv` | MCX - Commodity |

### Local Application URLs

| URL | Description |
|-----|-------------|
| `http://localhost:8080` | Web Dashboard (live during trading) |

---

## 3. Dependencies

Located in `requirements.txt`:

```
fyers-apiv3==3.1.8
flask==3.0.0
flask-cors==4.0.0
```

---

## 4. Product Types

Available product types for trading:

| Product | Description |
|---------|-------------|
| `CNC` | For equity only (Cash & Carry) |
| `INTRADAY` | Applicable for all segments |
| `MARGIN` | Applicable only for derivatives |
| `CO` | Cover Order |
| `BO` | Bracket Order |
| `MTF` | Margin Trading Facility |

---

## 5. Runtime Commands

### Setup & Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Token Generation (Daily - before market open)

```bash
# Generate new access token (expires at 6:00 AM IST daily)
python generate_token.py
```

### Running the Application

```bash
# Start the trading application
python main.py
```

---

## 6. Application Runtime Flow

### Step 1: Trading Mode Selection
```
1. Paper Trading (Simulated)
2. Real Trading (Live market - Real money)
```
- Press `1` for Paper Trading (recommended for testing)
- Press `2` for Real Trading (requires typing "yes" to confirm)

### Step 2: Instrument Selection
Select instrument by pressing keys 1-9 or A-Z:
```
1. NSE:NIFTY26FEB25000CE (NSE) [MARGIN]
2. NSE:NIFTY2620325200CE (NSE) [MARGIN]
...
```

### Step 3: Trading Commands (Single Keystroke - No Enter Required)

| Key | Action |
|-----|--------|
| `1`-`9` | Buy specified lots |
| `-1` to `-9` | Sell specified lots |
| `--` | Close all positions |
| `C` | Change instrument (only when flat) |
| `Q` | Quit application |

### Step 4: Web Dashboard
Access real-time dashboard at: **`http://localhost:8080`**

Features:
- Open Position panel with MTM P&L
- Order History
- Session Statistics (Paper Trading mode only)
- Trade Ledger with P&L metrics (Paper Trading mode only)
- CSV Export (Paper Trading mode only)
- Activity Logs

---

## 7. Files & Directories

### Project Structure

```
paper-trading-fyers/
├── main.py                 # Main application entry point
├── generate_token.py       # Token generation script
├── config.json             # Configuration (credentials, instruments)
├── requirements.txt        # Python dependencies
├── trading.log            # Application logs
├── fyersApi.log           # Fyers API logs
├── fyersRequests.log      # HTTP request logs
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

## 8. Important Notes

### Token Validity
- Access tokens expire at **6:00 AM IST daily**
- Generate a new token each trading day before running the application
- Run `python generate_token.py` to generate a new token

### Terminal Requirements
- The application requires a proper terminal (not IDE console) for raw input mode
- Run from terminal: `source venv/bin/activate && python main.py`

### Safety Warnings
- **Paper Trading**: Zero risk - simulated trades only
- **Real Trading**: Actual capital at risk - cannot undo orders

---

## 9. Troubleshooting

| Issue | Solution |
|-------|----------|
| Token expired | Run `python generate_token.py` to generate new token |
| Terminal not responding | Run from system terminal, not IDE console |
| Web dashboard not loading | Check if port 8080 is available |
| Orders not executing | Verify instrument symbol is active and trading |

---

## 10. Logs

```bash
# View application logs in real-time
tail -f trading.log

# Search for errors
grep ERROR trading.log

# Search for paper trading logs
grep "\[PAPER\]" trading.log
```

---

*Document generated for Paper Trading Fyers Application*
