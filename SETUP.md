# 🚀 Setup Instructions & Testing Guide

## Prerequisites

1. **Python 3.8 or higher**
   ```bash
   python3 --version
   ```

2. **Linux/Mac** (for terminal raw mode support)
   - Windows users: Use WSL or Git Bash

3. **Fyers Trading Account**
   - Active Fyers account
   - API access enabled

---

## Step-by-Step Setup

### Step 1: Create Project Directory

```bash
# Navigate to your preferred location
cd ~

# Create project directory
mkdir paper-trading-fyers
cd paper-trading-fyers
```

### Step 2: Copy All Project Files

Copy all the provided files maintaining the directory structure:

```
paper-trading-fyers/
├── main.py
├── config.json
├── generate_token.py
├── requirements.txt
├── README.md
├── SETUP.md (this file)
├── internal/
│   ├── __init__.py
│   ├── config.py
│   ├── logger.py
│   ├── position.py
│   ├── server.py
│   ├── terminal.py
│   └── trader.py
└── web/
    └── index.html
```

### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate     # On Windows
```

You should see `(venv)` in your terminal prompt.

### Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Expected output:
```
Successfully installed fyers-apiv3-3.1.8 flask-3.0.0 flask-cors-4.0.0
```

### Step 5: Configure Fyers API

1. **Create Fyers App:**
   - Go to https://myapi.fyers.in/dashboard/
   - Click "Create App"
   - Choose "Personal App"
   - Fill in details:
     - App Name: "Paper Trading App"
     - Redirect URI: `https://trade.fyers.in/api-login/redirect-uri/index.html`
     - Permissions: Select appropriate permissions
   - Note your `app_id` and `app_secret`

2. **Update config.json:**
   ```json
   {
     "app_id": "YOUR_APP_ID_HERE",
     "app_secret": "YOUR_APP_SECRET_HERE",
     "redirect_uri": "https://trade.fyers.in/api-login/redirect-uri/index.html",
     "access_token": "WILL_BE_GENERATED",
     "instruments": [
       {
         "symbol": "NSE:NIFTY26JAN25000CE",
         "exchange": "NSE",
         "lot_size": 65,
         "product": "MARGIN"
       }
     ]
   }
   ```

### Step 6: Generate Access Token

```bash
python generate_token.py
```

Follow the prompts:
1. Browser will open automatically
2. Login to Fyers
3. Copy the `auth_code` from redirected URL
4. Paste it when prompted
5. Access token will be saved to `config.json`

**Important:** Generate new token daily before market hours.

### Step 7: Update Instruments

Edit `config.json` and add your trading instruments:

```json
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
```

**Get current symbols from:**
- NSE F&O: https://public.fyers.in/sym_details/NSE_FO_sym_master.json
- NSE CM: https://public.fyers.in/sym_details/NSE_CM_sym_master.json

---

## Testing the Application

### Test 1: Paper Trading Mode (Safe)

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Start application
python main.py
```

**Expected Flow:**

1. **Mode Selection:**
   ```
   TRADING MODE SELECTION
   1. PAPER TRADING (Simulated - No real orders)
   2. REAL TRADING (Live orders - Real money)
   
   Select mode (1 for Paper, 2 for Real): 1
   Confirm PAPER TRADING mode? (yes/no): yes
   ```

2. **Instrument Selection:**
   ```
   === Available Instruments ===
   1. NSE:NIFTY26JAN25000CE (NSE) [MARGIN] - Lot Size: 65
   
   Select instrument (1-9, A-Z) or Q to quit:
   ```
   Press: `1`

3. **Trading Commands:**
   ```
   Ready. Enter commands:
   >
   ```
   
   Try these commands:
   - Press `2` → Buy 2 lots (paper)
   - Press `1` → Buy 1 more lot (paper)
   - Press `-3` → Sell 3 lots (paper, creates trade records)

4. **Web Dashboard:**
   - Open browser: http://localhost:8080
   - Verify:
     - ✅ Mode badge shows "PAPER TRADING" in green
     - ✅ Session Statistics visible
     - ✅ Trade Ledger visible
     - ✅ Positions update correctly
     - ✅ Orders show in history

5. **Export Trades:**
   - Click "Export CSV" button
   - Check `trades/` directory for CSV file
   - Verify trade data is correct

6. **Exit:**
   - Press `Q` in terminal
   - Verify trades exported automatically
   - Check `trading.log` for session summary

### Test 2: Verify Paper Trading Execution

**Important:** This tests that paper trading is truly simulated.

1. Start app in paper mode
2. Place several trades
3. Check Fyers account orderbook online
4. **Verify:** No actual orders appear in Fyers
5. **Verify:** Dashboard shows simulated trades
6. **Verify:** Logs show `[PAPER]` prefix

### Test 3: Price Accuracy Test

1. Start paper trading
2. Buy 1 lot
3. In another terminal:
   ```bash
   tail -f trading.log | grep "\[PAPER\]"
   ```
4. Check logged execution price
5. Compare with market depth on Fyers web
6. **Verify:** Price matches best ask/bid

### Test 4: Trade Matching Test (FIFO)

**Scenario:** Multiple buys, then partial sell

1. Buy 2 lots at price A
2. Buy 1 lot at price B
3. Sell 2 lots
4. **Verify:** Trade ledger shows:
   - First trade: 2 lots from price A
   - Second trade: 0 lots (partial)
5. **Verify:** 1 lot remains at price B

### Test 5: Real Trading Mode (Use with Caution!)

⚠️ **WARNING: This uses real money!**

Only test with:
- Minimal quantity (1 lot)
- Low-value instruments
- During market hours
- With sufficient funds

```bash
python main.py
Select mode: 2
⚠️ CONFIRM REAL TRADING MODE? (yes/no): yes
```

**Verify:**
- Mode badge shows "REAL TRADING" in red
- Session Statistics NOT visible
- Trade Ledger NOT visible
- Orders appear in Fyers account
- Real P&L impact

**After test:**
- Close position immediately
- Switch back to paper mode for practice

---

## Verification Checklist

### Setup Verification

- [ ] Python version 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed without errors
- [ ] All project files in correct locations
- [ ] `config.json` has valid credentials
- [ ] Access token generated successfully
- [ ] Instruments list updated for current week

### Functionality Verification

#### Paper Trading Mode
- [ ] Mode selection works correctly
- [ ] Instrument selection responsive
- [ ] Buy orders execute instantly
- [ ] Sell orders execute instantly
- [ ] Prices match market depth
- [ ] Position updates in real-time
- [ ] Trade ledger populates correctly
- [ ] Session statistics calculate properly
- [ ] CSV export creates valid file
- [ ] No orders in actual Fyers account
- [ ] Logs show `[PAPER]` prefix

#### Real Trading Mode (Optional)
- [ ] Warning shown on selection
- [ ] Confirmation required
- [ ] Orders execute on exchange
- [ ] Orders visible in Fyers account
- [ ] Real P&L impact
- [ ] Paper-specific features hidden

#### Web Dashboard
- [ ] Dashboard loads at localhost:8080
- [ ] Mode badge displays correctly
- [ ] Position updates every 5 seconds
- [ ] Order history displays
- [ ] Logs update in real-time
- [ ] Trade table sortable
- [ ] Export button functional
- [ ] No console errors in browser

### Error Handling

- [ ] Handles invalid instrument selection
- [ ] Prevents instrument change with open position
- [ ] Graceful shutdown on Ctrl+C
- [ ] Exports trades on exit
- [ ] Logs errors appropriately

---

## Common Issues and Solutions

### Issue 1: ModuleNotFoundError

**Error:** `ModuleNotFoundError: No module named 'internal'`

**Solution:**
```bash
# Ensure you're in the project root
pwd  # Should show: .../paper-trading-fyers

# Ensure virtual environment is activated
which python  # Should show: .../paper-trading-fyers/venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 2: Terminal Not Responding

**Error:** Keys don't register

**Solution:**
```bash
# Don't run from IDE
# Use actual terminal:
source venv/bin/activate
python main.py
```

### Issue 3: Access Token Expired

**Error:** `Authorization error` or `403`

**Solution:**
```bash
# Generate new token
python generate_token.py

# Tokens expire at 6 AM IST daily
```

### Issue 4: Web Dashboard Not Loading

**Error:** Cannot connect to localhost:8080

**Solution:**
```bash
# Check if port is in use
lsof -i :8080

# Kill existing process if needed
kill -9 <PID>

# Restart application
python main.py
```

### Issue 5: Trades Not Exporting

**Error:** Export button shows error

**Solution:**
```bash
# Create trades directory manually
mkdir -p trades

# Check permissions
ls -la trades/
```

---

## Performance Benchmarks

### Expected Performance

| Operation | Time |
|-----------|------|
| Order placement (paper) | < 200ms |
| Order placement (real) | < 500ms |
| Position update | < 100ms |
| Dashboard refresh | 500ms |
| Trade export | < 1s |

### Resource Usage

| Resource | Usage |
|----------|-------|
| Memory | ~50MB |
| CPU | < 5% idle, < 20% trading |
| Network | Minimal (API calls only) |

---

## Daily Usage Workflow

### Morning Routine (Before Market)

1. **Generate Token** (8:15-8:30 AM)
   ```bash
   cd ~/paper-trading-fyers
   source venv/bin/activate
   python generate_token.py
   ```

2. **Update Instruments** (8:30-9:00 AM)
   - Edit `config.json`
   - Update weekly expiry symbols
   - Verify lot sizes

3. **Start Application** (9:00 AM)
   ```bash
   python main.py
   ```

4. **Select Mode**
   - Paper: Practice and test
   - Real: Actual trading

5. **Open Dashboard**
   - Browser: http://localhost:8080
   - Position on second monitor

### During Trading

- Monitor dashboard for positions
- Use terminal for rapid execution
- Check logs for confirmations
- Export trades periodically

### End of Day

1. Close all positions
2. Export final trades (auto-exported on exit)
3. Review trade ledger
4. Analyze performance metrics
5. Press `Q` to quit gracefully

---

## Advanced Configuration

### Multiple Instruments Setup

For day trading with rapid instrument switching:

```json
"instruments": [
  // Current week contracts
  {"symbol": "NSE:NIFTY26JAN25000CE", "exchange": "NSE", "lot_size": 65, "product": "MARGIN"},
  {"symbol": "NSE:NIFTY26JAN25000PE", "exchange": "NSE", "lot_size": 65, "product": "MARGIN"},
  {"symbol": "NSE:BANKNIFTY26JAN58700CE", "exchange": "NSE", "lot_size": 30, "product": "MARGIN"},
  {"symbol": "NSE:BANKNIFTY26JAN58700PE", "exchange": "NSE", "lot_size": 30, "product": "MARGIN"},
  
  // ATM options
  {"symbol": "NSE:NIFTY26JAN25100CE", "exchange": "NSE", "lot_size": 65, "product": "INTRADAY"},
  {"symbol": "NSE:NIFTY26JAN25100PE", "exchange": "NSE", "lot_size": 65, "product": "INTRADAY"},
  
  // Equity for hedging
  {"symbol": "NSE:SBIN-EQ", "exchange": "NSE", "lot_size": 1, "product": "CNC"},
  {"symbol": "NSE:RELIANCE-EQ", "exchange": "NSE", "lot_size": 1, "product": "CNC"}
]
```

### Log File Management

```bash
# View real-time logs
tail -f trading.log

# Filter paper trading logs
grep "\[PAPER\]" trading.log

# Search for errors
grep "ERROR" trading.log

# Archive old logs
mv trading.log trading_$(date +%Y%m%d).log
```

---

## Next Steps

1. **Practice in Paper Mode**
   - Get comfortable with keyboard shortcuts
   - Test your trading strategy
   - Analyze trade results

2. **Backtest Your Strategy**
   - Export trades to CSV
   - Analyze in Excel/Python
   - Refine approach

3. **Graduate to Real Trading**
   - Start with minimal size
   - Increase gradually
   - Always verify mode before trading

---

## Support

For issues or questions:

1. Check `trading.log` for error messages
2. Review this SETUP.md document
3. Consult README.md for features
4. Check Fyers API documentation

---

**Happy Trading! 🚀📈**

Remember: Always start with paper trading to learn the system!