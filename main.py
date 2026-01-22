#!/usr/bin/env python3
"""
Paper Trading Application for Fyers
Ultra-low latency single-keystroke trading with Paper Trading Mode
"""

import sys
import os
import time
import signal
import threading
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from internal.config import Config
from internal.logger import Logger
from internal.position import PositionManager
from internal.server import WebServer
from internal.terminal import Terminal
from internal.trader import Trader, PaperTrader

from fyers_apiv3 import fyersModel

# Global state
cfg = None
fyers = None
pos_mgr = None
trader = None
server = None
logger = None
instrument = None
terminal = None
paper_mode = False

# Command state machine
cmd_state = ""
cmd_lock = threading.Lock()


def main():
    """Main application entry point"""
    global cfg, fyers, pos_mgr, trader, server, logger, instrument, terminal, paper_mode

    # Initialize logger first
    logger = Logger("trading.log")
    logger.info("=== Paper Trading Application Starting ===")

    # Load configuration
    try:
        cfg = Config.load("config.json")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        print(f"Failed to load config: {e}")
        sys.exit(1)

    # Initialize Fyers client
    fyers = fyersModel.FyersModel(
        client_id=cfg.app_id,
        token=cfg.access_token,
        is_async=False,
        log_path=""
    )

    # Verify credentials
    try:
        profile = fyers.get_profile()
        if profile['s'] == 'ok':
            logger.info(f"Logged in as: {profile['data']['name']} ({profile['data']['fy_id']})")
        else:
            raise Exception(f"Login failed: {profile.get('message', 'Unknown error')}")
    except Exception as e:
        logger.error(f"Failed to verify credentials: {e}")
        print(f"Failed to verify credentials: {e}")
        print("\nPlease generate a new access token using: python generate_token.py")
        sys.exit(1)

    # Initialize terminal for raw input
    terminal = Terminal()
    terminal.set_raw_mode()

    # Select trading mode
    paper_mode = select_trading_mode()
    
    if paper_mode:
        logger.info("=" * 60)
        logger.info("PAPER TRADING MODE - Simulated Trading")
        logger.info("=" * 60)
    else:
        logger.warning("=" * 60)
        logger.warning("REAL TRADING MODE - Live Trading with Real Money")
        logger.warning("=" * 60)

    # Initialize managers
    pos_mgr = PositionManager(paper_mode=paper_mode)

    # Select instrument
    instrument = select_instrument()

    # Initialize trader and server
    if paper_mode:
        trader = PaperTrader(fyers, pos_mgr, instrument, logger)
    else:
        trader = Trader(fyers, pos_mgr, instrument, logger)
    
    server = WebServer(pos_mgr, instrument, logger, paper_mode=paper_mode)

    # Start web server in background thread
    server_thread = threading.Thread(target=server.start, args=(8080,), daemon=True)
    server_thread.start()

    # Start position update loop
    update_thread = threading.Thread(target=update_position_loop, daemon=True)
    update_thread.start()

    # Setup graceful shutdown
    setup_graceful_shutdown()

    # Give web server time to start
    time.sleep(0.5)

    logger.info("Application ready. Waiting for commands...")
    print("")
    print("=== Web GUI: http://localhost:8080 ===")
    print("")
    print("Ready. Enter commands:")
    print("", end="", flush=True)  # Tab indentation for input

    # Start command loop
    command_loop()


def select_trading_mode():
    """Select trading mode with single keystroke"""
    global terminal, logger
    
    print("\n=== Trading Mode Selection ===")
    print("1. Paper Trading (Simulated)")
    print("2. Real Trading (Live market - Real money)")
    print("")
    print("Select mode (1 or 2): ", end="", flush=True)
    
    try:
        while True:
            char = terminal.read_char()
            
            if char == '1':
                print("1")
                print("")
                return True
            elif char == '2':
                print("2")
                print("")
                print("!" * 70)
                print("WARNING: REAL TRADING MODE")
                print("!" * 70)
                print("This will place REAL orders with REAL MONEY!")
                
                # Temporarily restore for text input
                terminal.restore()
                confirm = input("Type 'yes' to confirm: ").strip().lower()
                terminal.set_raw_mode()
                
                if confirm == 'yes':
                    return False
                else:
                    print("Cancelled. Switching to Paper Trading mode.")
                    return True
            elif char.upper() == 'Q' or ord(char) == 3:
                print("")
                print("Exiting application.")
                sys.exit(0)
    except KeyboardInterrupt:
        print("")
        print("Exiting application.")
        sys.exit(0)


def select_instrument():
    """Select trading instrument with single keystroke"""
    global cfg, logger, terminal

    print("")
    print("=== Available Instruments ===")
    for i, inst in enumerate(cfg.instruments):
        if i < 9:
            key = str(i + 1)
        else:
            key = chr(ord('A') + (i - 9))

        product = inst.product if inst.product else "INTRADAY"
        print(f"{key}. {inst.symbol} ({inst.exchange}) [{product}] - Lot Size: {inst.lot_size}")

    print("")
    print("Select instrument (1-9, A-Z) or Q to quit: ", end="", flush=True)

    try:
        while True:
            char = terminal.read_char()

            # Handle Quit
            if char.upper() == 'Q':
                print("")
                print("Exiting application.")
                sys.exit(0)

            # Handle 1-9
            if char.isdigit() and '1' <= char <= '9':
                idx = int(char) - 1
                if idx < len(cfg.instruments):
                    selected = cfg.instruments[idx]
                    print("")
                    print("")
                    print(f"Selected: {selected.symbol} ({selected.exchange}) [{selected.product}]")
                    logger.info(f"Selected instrument: {selected.symbol} ({selected.exchange}) [{selected.product}]")
                    return selected

            # Handle A-Z
            if char.upper().isalpha():
                idx = 9 + (ord(char.upper()) - ord('A'))
                if idx < len(cfg.instruments):
                    selected = cfg.instruments[idx]
                    print("")
                    print("")
                    print(f"Selected: {selected.symbol} ({selected.exchange}) [{selected.product}]")
                    logger.info(f"Selected instrument: {selected.symbol} ({selected.exchange}) [{selected.product}]")
                    return selected

    except KeyboardInterrupt:
        print("")
        print("Exiting application.")
        sys.exit(0)


def command_loop():
    """Main command processing loop with single-keystroke input"""
    global cmd_state, terminal, logger

    # Set terminal to raw mode for single-character input
    terminal.set_raw_mode()

    try:
        while True:
            char = terminal.read_char()

            # Handle Ctrl+C
            if ord(char) == 3:
                logger.info("Received Ctrl+C, exiting...")
                cleanup()
                sys.exit(0)

            # Handle Quit
            if char.upper() == 'Q':
                logger.info("Quit command received")
                cleanup()
                sys.exit(0)

            # Handle Change Instrument
            if char.upper() == 'C':
                handle_change_instrument()
                continue

            # Handle numeric input and minus
            if char.isdigit() or char == '-':
                handle_numeric_input(char)

    except KeyboardInterrupt:
        cleanup()
        sys.exit(0)


def handle_numeric_input(char):
    """Handle numeric command input with state machine"""
    global cmd_state, cmd_lock

    with cmd_lock:
        if cmd_state == "":
            # Initial state
            if char == '-':
                print("-", end="", flush=True)
                cmd_state = "-"
            elif '1' <= char <= '9':
                print(char, end="", flush=True)
                num = int(char)
                cmd_state = ""
                threading.Thread(target=place_buy_order, args=(num,), daemon=True).start()
            elif char == '0':
                print("0", end="", flush=True)
                cmd_state = ""

        elif cmd_state == "-":
            # Waiting for next character after minus
            if char == '-':
                print("-", end="", flush=True)
                cmd_state = ""
                threading.Thread(target=close_all_positions, daemon=True).start()
            elif '1' <= char <= '9':
                print(char, end="", flush=True)
                num = int(char)
                cmd_state = ""
                threading.Thread(target=place_sell_order, args=(num,), daemon=True).start()
            elif char == '0':
                print("0", end="", flush=True)
                cmd_state = ""
            else:
                cmd_state = ""


def handle_change_instrument():
    """Handle instrument change command"""
    global instrument, trader, server, pos_mgr, terminal, logger

    if pos_mgr.has_open_position():
        logger.warn("Cannot change instrument with open positions")
        print("")
        print("Cannot change with open positions")
        print("", end="", flush=True)
        server.broadcast_update()
        return

    # Position is flat, proceed with change
    pos_mgr.reset()
    logger.info("Changing instrument...")
    print("")
    instrument = select_instrument()
    trader.update_instrument(instrument)
    server.update_instrument(instrument)
    server.broadcast_update()

    # Put terminal back in raw mode
    terminal.set_raw_mode()

    print("")
    print("Ready. Enter commands:")
    print("", end="", flush=True)  # Tab indentation for input


def place_buy_order(lots):
    """Place buy order"""
    global trader, server, logger

    try:
        trader.place_order("BUY", lots)
        print("", end="", flush=True)
    except Exception as e:
        logger.error(f"Buy order failed: {e}")

    server.broadcast_update()


def place_sell_order(lots):
    """Place sell order"""
    global trader, server, logger

    try:
        trader.place_order("SELL", lots)
        print("", end="", flush=True)
    except Exception as e:
        logger.error(f"Sell order failed: {e}")

    server.broadcast_update()


def close_all_positions():
    """Close all open positions"""
    global pos_mgr, trader, server, logger

    lots = pos_mgr.get_open_lots()
    if lots <= 0:
        logger.warn("No open positions to close")
        server.broadcast_update()
        return

    logger.info(f"CLOSE ALL command: closing {lots} lots")
    try:
        trader.place_order("SELL", lots)
        print("", end="", flush=True)
    except Exception as e:
        logger.error(f"Close all failed: {e}")

    server.broadcast_update()


def update_position_loop():
    """Background thread to update position prices"""
    global pos_mgr, trader, server, logger

    while True:
        time.sleep(5)
        try:
            if pos_mgr.get_position()['qty_units'] > 0:
                price = trader.fetch_current_price()
                if price > 0:
                    pos_mgr.update_cmp(price)
                    server.broadcast_update()
        except Exception as e:
            logger.debug(f"Price fetch skipped: {e}")


def setup_graceful_shutdown():
    """Setup signal handlers for graceful shutdown"""
    global paper_mode

    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        
        # Export trades if paper mode
        if paper_mode and pos_mgr:
            try:
                filepath = pos_mgr.export_session_trades()
                if filepath:
                    print(f"\nTrades exported: {filepath}")
            except Exception as e:
                logger.error(f"Failed to export trades: {e}")
        
        cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def cleanup():
    """Cleanup resources"""
    global terminal, logger

    logger.info("Cleaning up resources...")

    # Restore terminal
    if terminal:
        terminal.restore()

    # Close logger
    if logger:
        logger.close()

    print("\nGoodbye!")


if __name__ == "__main__":
    main()