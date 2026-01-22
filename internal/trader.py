"""
Order execution and trading logic with Paper Trading support
"""
import time
from datetime import datetime
from fyers_apiv3 import fyersModel


class Trader:
    """Handles real order placement and execution"""
    
    def __init__(self, fyers_client, pos_mgr, instrument, logger):
        self.fyers = fyers_client
        self.pos_mgr = pos_mgr
        self.instrument = instrument
        self.logger = logger
        self.last_order_time = time.time()
    
    def place_order(self, side: str, lots: int):
        """Place market order"""
        # Validate inputs
        if lots <= 0:
            self.logger.error(f"Invalid lots quantity: {lots}")
            raise ValueError("Lots must be greater than 0")
        
        if side not in ("BUY", "SELL"):
            self.logger.error(f"Invalid side: {side}")
            raise ValueError("Side must be 'BUY' or 'SELL'")
        
        # Rate limiting
        elapsed = time.time() - self.last_order_time
        if elapsed < 0.1:  # 100ms between orders
            time.sleep(0.1 - elapsed)
        self.last_order_time = time.time()
        
        quantity = lots * self.instrument.lot_size
        
        self.logger.info(f"Placing {side} order for {lots} lots ({quantity} units) of {self.instrument.symbol}")
        
        # Prepare order data
        order_data = {
            "symbol": self.instrument.symbol,
            "qty": quantity,
            "type": 2,  # Market order
            "side": 1 if side == "BUY" else -1,
            "productType": self.instrument.product,
            "limitPrice": 0,
            "stopPrice": 0,
            "validity": "DAY",
            "disclosedQty": 0,
            "offlineOrder": False,
            "stopLoss": 0,
            "takeProfit": 0
        }
        
        # Place order
        try:
            response = self.fyers.place_order(data=order_data)
            
            if response['s'] == 'ok':
                order_id = response.get('id', '')
                self.logger.info(f"Order placed successfully! Order ID: {order_id}")
                
                # Wait and fetch order details
                time.sleep(0.5)
                self._update_order_details(order_id, side, lots)
            else:
                error_msg = response.get('message', 'Unknown error')
                self.logger.error(f"Order placement failed: {error_msg}")
                raise Exception(f"Order failed: {error_msg}")
                
        except Exception as e:
            self.logger.error(f"Order placement exception: {e}")
            raise
    
    def _update_order_details(self, order_id: str, side: str, lots: int):
        """Fetch and update order execution details"""
        try:
            # Get order book
            orders_response = self.fyers.orderbook()
            
            if orders_response['s'] == 'ok':
                orderbook = orders_response.get('orderBook', [])
                
                # Find our order
                for order in orderbook:
                    if order.get('id') == order_id:
                        filled_qty = order.get('filledQty', 0)
                        avg_price = order.get('tradedPrice', 0)
                        status = order.get('status', 0)
                        
                        if filled_qty > 0 and avg_price > 0:
                            filled_lots = filled_qty // self.instrument.lot_size
                            
                            # Add to order history
                            from internal.position import Order
                            order_obj = Order(
                                timestamp=datetime.now(),
                                order_type=side,
                                quantity=filled_lots,
                                price=avg_price,
                                order_id=order_id,
                                status=self._get_status_text(status)
                            )
                            self.pos_mgr.add_order(order_obj)
                            
                            # Update position
                            self.pos_mgr.update_position(side, filled_lots, avg_price, self.instrument.lot_size)
                            
                            self.logger.info(f"Order executed: {filled_lots} lots @ ₹{avg_price:.2f}")
                            return
        
        except Exception as e:
            self.logger.warn(f"Could not fetch order details: {e}")
    
    def fetch_current_price(self) -> float:
        """Fetch current market price"""
        try:
            response = self.fyers.quotes(data={"symbols": self.instrument.symbol})
            
            if response['s'] == 'ok' and 'd' in response:
                for item in response['d']:
                    if item.get('n') == self.instrument.symbol and item.get('s') == 'ok':
                        ltp = item['v'].get('lp', 0)
                        if ltp > 0:
                            return ltp
            
            return 0
        except Exception as e:
            self.logger.debug(f"Price fetch failed: {e}")
            return 0
    
    def update_instrument(self, instrument):
        """Update trading instrument"""
        self.instrument = instrument
        self.logger.info(f"Instrument updated to: {instrument.symbol} ({instrument.exchange}) [{instrument.product}]")
    
    @staticmethod
    def _get_status_text(status: int) -> str:
        """Convert status code to text"""
        status_map = {
            1: "Cancelled",
            2: "Traded",
            4: "Transit",
            5: "Rejected",
            6: "Pending",
            7: "Expired"
        }
        return status_map.get(status, "Unknown")


class PaperTrader(Trader):
    """Handles simulated paper trading order execution"""
    
    def __init__(self, fyers_client, pos_mgr, instrument, logger):
        super().__init__(fyers_client, pos_mgr, instrument, logger)
        self.order_counter = 1
    
    def place_order(self, side: str, lots: int):
        """Place simulated paper trading order"""
        # Validate inputs
        if lots <= 0:
            self.logger.error(f"[PAPER] Invalid lots quantity: {lots}")
            raise ValueError("Lots must be greater than 0")
        
        if side not in ("BUY", "SELL"):
            self.logger.error(f"[PAPER] Invalid side: {side}")
            raise ValueError("Side must be 'BUY' or 'SELL'")
        
        # Rate limiting (for realism)
        elapsed = time.time() - self.last_order_time
        if elapsed < 0.1:
            time.sleep(0.1 - elapsed)
        self.last_order_time = time.time()
        
        quantity = lots * self.instrument.lot_size
        
        self.logger.info(f"[PAPER] Placing {side} order for {lots} lots ({quantity} units) of {self.instrument.symbol}")
        
        try:
            # Fetch market depth to get best bid/ask
            depth_response = self.fyers.depth(
                data={"symbol": self.instrument.symbol, "ohlcv_flag": 1}
            )
            
            if depth_response.get('s') != 'ok':
                error_msg = depth_response.get('message', 'Unknown error')
                raise Exception(f"Failed to fetch market depth: {error_msg}")
            
            depth_data = depth_response.get('d', {}).get(self.instrument.symbol, {})
            
            if not depth_data:
                raise Exception(f"No market depth data available for {self.instrument.symbol}")
            
            # Determine execution price based on order side
            exec_price = 0
            
            if side == "BUY":
                # For BUY, use best ASK price (what sellers are offering)
                ask_prices = depth_data.get('ask', [])
                if ask_prices and len(ask_prices) > 0:
                    exec_price = ask_prices[0].get('price', 0)
                
                # Fallback to LTP if no ask available
                if exec_price <= 0:
                    exec_price = depth_data.get('ltp', 0)
                
                if exec_price <= 0:
                    raise Exception("Could not determine execution price - no ASK or LTP available")
                
            else:  # SELL
                # For SELL, use best BID price (what buyers are offering)
                bid_prices = depth_data.get('bids', [])
                if bid_prices and len(bid_prices) > 0:
                    exec_price = bid_prices[0].get('price', 0)
                
                # Fallback to LTP if no bid available
                if exec_price <= 0:
                    exec_price = depth_data.get('ltp', 0)
                
                if exec_price <= 0:
                    raise Exception("Could not determine execution price - no BID or LTP available")
            
            # Validate execution price is reasonable
            if exec_price <= 0:
                raise Exception(f"Invalid execution price: {exec_price}")
            
            # Simulate order execution
            order_id = f"PAPER{self.order_counter:06d}"
            self.order_counter += 1
            
            self.logger.info(f"[PAPER] Order executed: {lots} lots @ ₹{exec_price:.2f} (Order ID: {order_id})")
            
            # Add to order history
            from internal.position import Order
            order_obj = Order(
                timestamp=datetime.now(),
                order_type=side,
                quantity=lots,
                price=exec_price,
                order_id=order_id,
                status="Paper Executed"
            )
            self.pos_mgr.add_order(order_obj)
            
            # Update position
            self.pos_mgr.update_position(side, lots, exec_price, self.instrument.lot_size)
            
        except KeyError as e:
            self.logger.error(f"[PAPER] Missing expected data in market depth response: {e}")
            raise Exception(f"Invalid market depth data structure: {e}")
        except Exception as e:
            self.logger.error(f"[PAPER] Order execution failed: {e}")
            raise
    
    def fetch_current_price(self) -> float:
        """Fetch current market price (same as real trader)"""
        return super().fetch_current_price()