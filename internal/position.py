"""
Position and order management with Paper Trading support
"""

import threading
import csv
import logging
from datetime import datetime
from typing import List, Dict
from pathlib import Path


class Order:
    """Represents a single order"""

    def __init__(self, timestamp: datetime, order_type: str, quantity: int,
                 price: float, order_id: str, status: str = ""):
        self.timestamp = timestamp
        self.order_type = order_type  # BUY or SELL
        self.quantity = quantity
        self.price = price
        self.order_id = order_id
        self.status = status

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'type': self.order_type,
            'quantity': self.quantity,
            'price': self.price,
            'order_id': self.order_id,
            'status': self.status
        }


class Trade:
    """Represents a completed round-trip trade"""
    
    def __init__(self, entry_time: datetime, entry_price: float, entry_qty: int,
                 exit_time: datetime, exit_price: float, exit_qty: int):
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.entry_qty = entry_qty
        self.exit_time = exit_time
        self.exit_price = exit_price
        self.exit_qty = exit_qty
        
        # Calculate trade metrics
        self.qty = min(entry_qty, exit_qty)  # Actual traded quantity
        self.pnl = (exit_price - entry_price) * self.qty
        self.pnl_percent = ((exit_price - entry_price) / entry_price) * 100 if entry_price > 0 else 0
        self.duration_seconds = (exit_time - entry_time).total_seconds()
        self.turnover = (entry_price + exit_price) * self.qty
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'entry_time': self.entry_time.strftime('%Y-%m-%d %H:%M:%S'),
            'entry_price': round(self.entry_price, 2),
            'entry_qty': self.entry_qty,
            'exit_time': self.exit_time.strftime('%Y-%m-%d %H:%M:%S'),
            'exit_price': round(self.exit_price, 2),
            'exit_qty': self.exit_qty,
            'qty': self.qty,
            'pnl': round(self.pnl, 2),
            'pnl_percent': round(self.pnl_percent, 2),
            'duration_seconds': int(self.duration_seconds),
            'turnover': round(self.turnover, 2)
        }


class Position:
    """Current position state"""

    def __init__(self):
        self.qty_lots = 0
        self.qty_units = 0
        self.total_value = 0.0
        self.avg_price = 0.0
        self.cmp = 0.0  # Current market price
        self.mtm = 0.0  # Mark to market P&L
        self.mtm_change_percent = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'qty_lots': self.qty_lots,
            'qty_units': self.qty_units,
            'total_value': round(self.total_value, 2),
            'avg_price': round(self.avg_price, 2),
            'cmp': round(self.cmp, 2),
            'mtm': round(self.mtm, 2),
            'mtm_change_percent': round(self.mtm_change_percent, 2)
        }
    
    @property
    def net_lots(self):
        """Return net position in lots (positive for long, negative for short)"""
        return self.qty_lots


class PositionManager:
    """Manages positions and order history with Paper Trading support"""

    def __init__(self, paper_mode: bool = False):
        self.lock = threading.Lock()
        self.position = Position()
        self.order_history: List[Order] = []
        self.trade_history: List[Trade] = []
        self.total_buy_cost = 0.0
        self.total_buy_units = 0
        self.paper_mode = paper_mode
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Paper trading specific
        self.session_net_pnl = 0.0
        self.pending_buy_orders = []  # List of (timestamp, price, qty) for FIFO matching

    def add_order(self, order: Order):
        """Add order to history"""
        with self.lock:
            self.order_history.append(order)

    def update_position(self, txn_type: str, lots: int, price: float, lot_size: int):
        """Update position after trade"""
        with self.lock:
            units = lots * lot_size
            value = units * price

            if txn_type == "BUY":
                # Track cumulative buy cost
                self.total_buy_cost += value
                self.total_buy_units += units

                # Update position
                self.position.qty_units += units
                self.position.qty_lots += lots

                # Recalculate average price
                if self.total_buy_units > 0:
                    self.position.avg_price = self.total_buy_cost / self.total_buy_units

                # Update total value
                self.position.total_value = self.position.qty_units * self.position.avg_price
                
                # Track for trade matching (FIFO)
                if self.paper_mode:
                    self.pending_buy_orders.append({
                        'timestamp': datetime.now(),
                        'price': price,
                        'qty': units
                    })

            else:  # SELL
                # Match with pending buys for trade history (FIFO)
                if self.paper_mode:
                    self._match_and_create_trades(units, price)
                
                self.position.qty_units -= units
                self.position.qty_lots -= lots

                # Reduce tracked buy cost proportionally
                if self.total_buy_units > 0:
                    cost_reduction = (units / self.total_buy_units) * self.total_buy_cost
                    self.total_buy_cost -= cost_reduction
                    self.total_buy_units -= units

                # Reset if position is fully closed
                if self.position.qty_units <= 0:
                    self.position.qty_units = 0
                    self.position.qty_lots = 0
                    self.position.total_value = 0
                    self.position.avg_price = 0
                    self.position.mtm = 0
                    self.position.mtm_change_percent = 0
                    self.total_buy_cost = 0
                    self.total_buy_units = 0
                else:
                    # Recalculate for remaining position
                    self.position.total_value = self.position.qty_units * self.position.avg_price

            # Recalculate MTM with current CMP if available
            if self.position.cmp > 0 and self.position.qty_units > 0:
                self._calculate_mtm()

    def _match_and_create_trades(self, sell_qty: int, sell_price: float):
        """Match sell with pending buys (LIFO) and create single trade record with averaged buy price"""
        if sell_qty <= 0:
            self.logger.warning(f"Invalid sell quantity for trade matching: {sell_qty}")
            return
        
        if sell_price <= 0:
            self.logger.warning(f"Invalid sell price for trade matching: {sell_price}")
            return
        
        remaining_qty = sell_qty
        exit_time = datetime.now()
        
        # Collect all matched buys for averaging (LIFO - start from end)
        total_matched_qty = 0
        total_buy_value = 0.0
        earliest_entry_time = None
        
        # Work backwards through pending buys (LIFO)
        idx = len(self.pending_buy_orders) - 1
        
        while remaining_qty > 0 and idx >= 0:
            buy_order = self.pending_buy_orders[idx]
            
            matched_qty = min(remaining_qty, buy_order['qty'])
            
            if matched_qty > 0:
                total_matched_qty += matched_qty
                total_buy_value += matched_qty * buy_order['price']
                
                # Track earliest entry time (for the aggregated trade)
                if earliest_entry_time is None or buy_order['timestamp'] < earliest_entry_time:
                    earliest_entry_time = buy_order['timestamp']
                
                # Update buy order quantity
                buy_order['qty'] -= matched_qty
                remaining_qty -= matched_qty
                
                # Remove if fully consumed
                if buy_order['qty'] <= 0:
                    self.pending_buy_orders.pop(idx)
            
            idx -= 1
        
        # Create single trade record with averaged buy price
        if total_matched_qty > 0 and total_buy_value > 0:
            avg_buy_price = total_buy_value / total_matched_qty
            
            try:
                trade = Trade(
                    entry_time=earliest_entry_time,
                    entry_price=avg_buy_price,
                    entry_qty=total_matched_qty,
                    exit_time=exit_time,
                    exit_price=sell_price,
                    exit_qty=total_matched_qty
                )
                self.trade_history.append(trade)
                
                # Update session net P&L
                self.session_net_pnl += trade.pnl
            except Exception as e:
                # Log but don't fail
                self.logger.error(f"Error creating trade record: {e}")

    def update_cmp(self, price: float):
        """Update current market price"""
        with self.lock:
            self.position.cmp = price
            if self.position.qty_units > 0:
                self._calculate_mtm()

    def _calculate_mtm(self):
        """Calculate mark-to-market P&L (must be called with lock held)"""
        if self.position.qty_units <= 0:
            self.position.mtm = 0
            self.position.mtm_change_percent = 0
            return

        current_value = self.position.qty_units * self.position.cmp
        self.position.mtm = current_value - self.position.total_value

        if self.position.total_value > 0:
            self.position.mtm_change_percent = (self.position.mtm / self.position.total_value) * 100
        else:
            self.position.mtm_change_percent = 0

    def get_position(self) -> Dict:
        """Get current position"""
        with self.lock:
            return self.position.to_dict()

    def get_order_history(self) -> List[Dict]:
        """Get order history"""
        with self.lock:
            return [order.to_dict() for order in self.order_history]
    
    def get_trade_history(self) -> List[Dict]:
        """Get completed trade history"""
        with self.lock:
            return [trade.to_dict() for trade in self.trade_history]
    
    def get_session_stats(self) -> Dict:
        """Get session trading statistics"""
        with self.lock:
            total_trades = len(self.trade_history)
            winning_trades = sum(1 for t in self.trade_history if t.pnl > 0)
            losing_trades = sum(1 for t in self.trade_history if t.pnl < 0)
            
            total_turnover = sum(t.turnover for t in self.trade_history)
            avg_pnl = self.session_net_pnl / total_trades if total_trades > 0 else 0
            
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            return {
                'net_pnl': round(self.session_net_pnl, 2),
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': round(win_rate, 2),
                'total_turnover': round(total_turnover, 2),
                'avg_pnl': round(avg_pnl, 2)
            }

    def get_open_lots(self) -> int:
        """Get open lots count"""
        with self.lock:
            return self.position.qty_lots

    def has_open_position(self) -> bool:
        """Check if there's an open position"""
        with self.lock:
            return self.position.qty_units != 0

    def reset(self):
        """Reset all positions and history"""
        with self.lock:
            self.position = Position()
            self.order_history = []
            # Don't reset trade_history in paper mode - keep session history
            if not self.paper_mode:
                self.trade_history = []
                self.session_net_pnl = 0.0
            self.total_buy_cost = 0
            self.total_buy_units = 0
            self.pending_buy_orders = []
    
    def export_session_trades(self, filepath: str = None) -> str:
        """Export session trades to CSV file"""
        if not filepath:
            # Create trades directory if it doesn't exist
            trades_dir = Path("trades")
            try:
                trades_dir.mkdir(exist_ok=True)
            except Exception as e:
                self.logger.error(f"Failed to create trades directory: {e}")
                return ""
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = trades_dir / f"paper_trades_{timestamp}.csv"
        
        with self.lock:
            if len(self.trade_history) == 0:
                return ""
            
            try:
                # Write to CSV
                with open(filepath, 'w', newline='') as csvfile:
                    fieldnames = ['entry_time', 'entry_price', 'entry_qty', 
                                'exit_time', 'exit_price', 'exit_qty', 'qty',
                                'pnl', 'pnl_percent', 'duration_seconds', 'turnover']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for trade in self.trade_history:
                        writer.writerow(trade.to_dict())
                
                return str(filepath)
            except Exception as e:
                self.logger.error(f"Failed to export trades: {e}")
                return ""