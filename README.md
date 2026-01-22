# 🚀 Paper Trading Application - Fyers Edition

**Ultra-Low Latency | Single-Keystroke Trading | Paper Trading Mode | Web Dashboard | Python-Based**

---

## 🎯 What This Application Offers

### ⚡ **Dual Trading Modes**

* **PAPER TRADING** - Simulated trading with no real money at risk
* **REAL TRADING** - Live order execution with actual capital
* Switch between modes at startup with confirmation

### ⚡ **Instant Single-Keystroke Trading**

* No `Enter` key — every action is **immediate**
* Buy, sell, close, change instruments, quit — all with **single keys**
* Raw terminal input for zero latency

### ⚡ **Instant Instrument Selection**

* Select instruments using **1–9, A–Z**
* Supports **up to 35 instruments**
* Case-insensitive (`a` = `A`)
* Press `Q` anytime to exit

### 🧼 **Silent Console, Full Visibility**

* Console goes silent after selection
* **Everything logged** to `trading.log`
* Real-time **log viewer in Web UI**
* Clean, distraction-free trading

### 📊 **Paper Trading Features**

* **Realistic Execution** - Uses best bid/ask prices from market depth
* **Trade Ledger** - Complete history of all round-trip trades
* **Session Statistics** - Net P&L, win rate, total trades, and more
* **CSV Export** - Export all trades for analysis
* **FIFO Matching** - Accurate P&L calculation for partial exits

### 🆓 **Fyers API - Free Tier Compatible**

* Position tracking via **executed order prices**
* Fully usable for **real trading**
* No WebSocket required for basic functionality

### 📈 **Optimized for Options & Equities**

* NIFTY / BANKNIFTY / Equity supported
* INTRADAY / MARGIN / CNC products
* Intraday + positional strategies

---

## 📁 Project Structure

```
paper-trading-fyers/
├── main.py
├── config.json
├── trading.log
├── generate_token.py
├── internal/
│   ├── __init__.py
│   ├── config.py
│   ├── logger.py
│   ├── position.py
│   ├── server.py
│   ├── terminal.py
│   └── trader.py
├── web/
│   └── index.html
├── trades/                    # Auto-created for CSV exports
│   └── paper_trades_*.csv
└── requirements.txt
```

---

## 🚀 Quick Start

### 1️⃣ Create Project

```bash
mkdir -p ~/paper-trading-fyers
cd ~/paper-trading-fyers

# Copy all files from the repository to this directory

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Setup Configuration

1. Edit `config.json` with your Fyers API credentials
2. Update instruments list with your trading symbols
3. Generate access token (see below)

---

## 🔐 Fyers API Setup

1. Visit [https://myapi.fyers.in/dashboard/](https://myapi.fyers.in/dashboard/)
2. Create **Personal App**
3. Get `app_id`, `app_secret`, `redirect_uri`
4. Update `config.json`

### Generate Access Token

```bash
python generate_token.py
```

**Note:** Access tokens expire at 6:00 AM IST daily. Generate a new token each trading day.

---

## ⚡ Trading Mode Selection

When you start the application, you'll be prompted:

```
==============================================================
TRADING MODE SELECTION
==============================================================

1. PAPER TRADING (Simulated - No real orders)
2. REAL TRADING (Live orders - Real money)

==============================================================
Select mode (1 for Paper, 2 for Real):
```

### Paper Trading Mode
* All orders are simulated
* Uses real market bid/ask prices
* No real money at risk
* Perfect for testing strategies
* Complete trade history with metrics

### Real Trading Mode
* Live order execution
* Real capital at risk
* Actual P&L impact
* Requires careful consideration

---

## ⚡ Instrument Selection – Single Keystroke

### Key Mapping

| Instrument # | Key     |
| ------------ | ------- |
| 1–9          | `1`–`9` |
| 10–35        | `A`–`Z` |
| Quit         | `Q`     |

**Maximum instruments:** 35

---

## 🎮 Trading Commands (No Enter Ever)

| Key       | Action              |
| --------- | ------------------- |
| `1`–`9`   | Buy lots            |
| `-1`–`-9` | Sell lots           |
| `--`      | Close all positions |
| `C`       | Change instrument   |
| `Q`       | Quit app            |

**Console stays silent — use Web UI**

---

## 🌐 Web Dashboard

### 📊 Features

#### All Modes:
* Real-time Positions Panel
* Live MTM P&L (₹ and %)
* Order History
* Activity Logs (Live)
* Auto-scroll

#### Paper Trading Only:
* **Session Statistics** - Net P&L, total trades, win rate
* **Trade Ledger** - Complete round-trip trade history with:
  * Entry/Exit timestamps
  * Entry/Exit prices
  * Quantity traded
  * Duration in seconds
  * P&L amount and percentage
  * Total turnover
* **CSV Export** - One-click trade export
* **Visual Indicators** - Color-coded wins/losses

### Access Dashboard

```
http://localhost:8080
```

---

## 📊 Paper Trading Execution Logic

### BUY Orders
1. Fetches market depth from Fyers
2. Uses **best ASK price** (seller's offer)
3. Records trade at that price
4. Updates position immediately

### SELL Orders
1. Fetches market depth from Fyers
2. Uses **best BID price** (buyer's offer)
3. Records trade at that price
4. Matches with pending buys (FIFO)
5. Creates trade record with P&L

### Price Updates
* Continues to fetch real-time LTP
* Updates MTM P&L for open positions
* Same as real trading mode

---

## 📝 Trade History & Analytics

### Session Statistics (Paper Mode)

Displayed in real-time on dashboard:

* **Net P&L** - Total profit/loss for the session
* **Total Trades** - Number of completed round trips
* **Win Rate** - Percentage of profitable trades
* **Winning/Losing Trades** - Count of each
* **Total Turnover** - Sum of all trade values

### Trade Ledger

Each completed trade shows:

| Column | Description |
|--------|-------------|
| Entry Time | Timestamp of position entry |
| Entry Price | Average entry price |
| Exit Time | Timestamp of position exit |
| Exit Price | Average exit price |
| Qty | Quantity traded |
| Duration | Time in trade (seconds) |
| P&L | Profit/Loss amount |
| P&L % | Profit/Loss percentage |
| Turnover | Total value transacted |

### CSV Export

* Click **"Export CSV"** button in dashboard
* Trades saved to `trades/paper_trades_YYYYMMDD_HHMMSS.csv`
* Import into Excel, Google Sheets, or analysis tools
* Automatic export on application exit

---

## 🔄 Change Instrument During Trading

Press `C` (only when no open positions):

```
=== Available Instruments ===
1. NSE:NIFTY26JAN25100CE [MARGIN]
2. NSE:BANKNIFTY26JAN58700CE [INTRADAY]

Select instrument (1-9, A-Z) or Q to quit: 2
```

---

## 🧠 Best Practices

### Organize Instruments

* 1–3 → Intraday options
* 4–6 → Positional
* 7–9 → Equity

### Daily Routine

1. Generate token (8:30 AM) - `python generate_token.py`
2. Update weekly expiry symbols in `config.json`
3. Start app before market open - `python main.py`
4. Select **Paper** or **Real** mode carefully
5. Monitor dashboard at `http://localhost:8080`

### Paper Trading Tips

* Test new strategies risk-free
* Practice order execution
* Understand market depth impact
* Analyze trade history for patterns
* Export and review performance metrics

---

## 📝 Example config.json

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

## Product Type (possible values)

* **CNC** - For equity only
* **INTRADAY** - Applicable for all segments
* **MARGIN** - Applicable only for derivatives
* **CO** - Cover Order
* **BO** - Bracket Order
* **MTF** - Margin Trading Facility

---

## 📝 Logs

```bash
# View logs in real-time
tail -f trading.log

# Search for errors
grep ERROR trading.log

# Search for paper trading specific logs
grep "\[PAPER\]" trading.log
```

---

## 🎓 Example Trading Sessions

### Paper Trading Session
```
python main.py

Select mode: 1 (Paper Trading)
Press: 1 → Select first instrument
Press: 2 → Buy 2 lots (simulated at best ask)
Press: 1 → Buy 1 more lot
Press: -3 → Sell 3 lots (simulated at best bid, creates trade records)

View dashboard → See trade history with P&L
Click Export → Download trades CSV
```

### Real Trading Session
```
python main.py

Select mode: 2 (Real Trading)
⚠️ Confirm: yes
Press: 1 → Select first instrument
Press: 1 → Buy 1 lot (REAL ORDER)
Press: -1 → Sell 1 lot (REAL ORDER)
```

---

## 🔧 Troubleshooting

### Issue: "FileNotFoundError: web/index.html"

**Solution:**
```bash
# Verify file structure
ls -la web/index.html
ls -la internal/trader.py

# Ensure all files are in correct locations
```

### Issue: Terminal not responding to keystrokes

**Cause:** IDE console doesn't support raw terminal mode.

**Solution:** Run from a proper terminal:
```bash
# From system terminal, not IDE console
cd ~/paper-trading-fyers
source venv/bin/activate
python main.py
```

### Issue: Paper trading shows wrong prices

**Cause:** Market depth fetch may have failed.

**Solution:** Check:
1. Valid access token
2. Symbol exists and is trading
3. Internet connection
4. Check `trading.log` for "[PAPER]" entries

### Issue: Trade history not showing

**Cause:** No completed round-trip trades yet.

**Solution:**
1. Ensure you've both bought AND sold
2. Check position is fully closed
3. Refresh dashboard

---

## ✅ Setup Verification Checklist

* [ ] Python 3.8+
* [ ] Virtual environment created and activated
* [ ] All dependencies installed (`pip install -r requirements.txt`)
* [ ] Fyers app created
* [ ] `config.json` updated with credentials
* [ ] Token generated with `generate_token.py`
* [ ] Weekly symbols updated in `config.json`
* [ ] Run from proper terminal (not IDE)
* [ ] Select Paper/Real mode at startup
* [ ] Web UI opens at http://localhost:8080
* [ ] Test order works

---

## 📊 Trade Analytics

### Analyzing Exported Data

After exporting trades to CSV, you can analyze:

1. **Win Rate** = (Winning Trades / Total Trades) × 100
2. **Average Win** = Sum of winning P&L / Winning trades
3. **Average Loss** = Sum of losing P&L / Losing trades
4. **Risk-Reward Ratio** = Average Win / Average Loss
5. **Profit Factor** = Gross Profit / Gross Loss
6. **Average Trade Duration** = Total duration / Total trades

### Excel/Google Sheets Formulas

```excel
# Win Rate
=COUNTIF(H:H,">0")/COUNTA(H:H)*100

# Average Win
=AVERAGEIF(H:H,">0")

# Average Loss
=AVERAGEIF(H:H,"<0")

# Profit Factor
=SUMIF(H:H,">0")/ABS(SUMIF(H:H,"<0"))
```

---

## 🔒 Important Safety Notes

### Paper Trading
* ✅ No real money at risk
* ✅ Perfect for learning and testing
* ✅ Unlimited practice
* ⚠️ Slippage may differ from real execution

### Real Trading
* ⚠️ Uses actual capital
* ⚠️ Real P&L impact
* ⚠️ Cannot undo executed orders
* ⚠️ Always verify before confirming mode

---

## 🤝 Support & Resources

* **Fyers API Docs**: https://myapi.fyers.in/docsv3
* **Symbol Master**: https://public.fyers.in/sym_details/
* **Community**: FYERS API & Algo community forum

---

## 📜 License

This is a trading utility application. Use at your own risk. No warranty provided.

---

## 🎯 Key Differences from Original App

| Feature | Original App | Paper Trading App |
|---------|--------------|-------------------|
| Order Execution | Real orders via Fyers API | Simulated using market depth |
| Risk | Real capital | Zero risk |
| Trade History | Order history only | Complete trade ledger |
| Analytics | Basic position tracking | Full session statistics |
| P&L Tracking | Real-time MTM | Real-time MTM + realized P&L |
| Export | None | CSV export of all trades |
| Mode Selection | N/A | Paper/Real choice at startup |

---

**Happy Paper Trading! 🚀📈**