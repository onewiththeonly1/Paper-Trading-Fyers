"""
Web server for dashboard with Paper Trading support
"""
import json
import os
import threading
import time
import traceback
from pathlib import Path
from flask import Flask, send_file, jsonify, send_from_directory
from flask_cors import CORS
import logging


class WebServer:
    """Flask-based web server for trading dashboard"""
    
    def __init__(self, pos_mgr, instrument, logger, paper_mode=False):
        self.pos_mgr = pos_mgr
        self.instrument = instrument
        self.logger = logger
        self.paper_mode = paper_mode
        self.port = None
        self.server_thread = None
        
        # Disable Flask's default logging to console
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        
        # Get the project root directory (parent of internal/)
        self.project_root = Path(__file__).parent.parent
        
        self.app = Flask(__name__, 
                        static_folder=str(self.project_root / 'web'),
                        static_url_path='')
        
        # Enable CORS for all routes
        CORS(self.app, resources={r"/api/*": {"origins": "*"}})
        
        self.ws_clients = []
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def home():
            try:
                # Use absolute path from project root
                html_path = self.project_root / 'web' / 'index.html'
                if not html_path.exists():
                    self.logger.error(f"index.html not found at {html_path}")
                    return f"Error: index.html not found at {html_path}", 404
                return send_file(str(html_path))
            except Exception as e:
                self.logger.error(f"Error serving index.html: {e}")
                self.logger.error(traceback.format_exc())
                return f"Error serving index.html: {e}", 500
        
        @self.app.route('/api/state')
        def get_state():
            try:
                data = self._get_state_data()
                return jsonify(data)
            except Exception as e:
                self.logger.error(f"Error in /api/state: {e}")
                self.logger.error(traceback.format_exc())
                return jsonify({
                    'error': str(e),
                    'position': {'qty_lots': 0, 'qty_units': 0, 'avg_price': 0, 'cmp': 0, 'total_value': 0, 'mtm': 0, 'mtm_change_percent': 0},
                    'orderHistory': [],
                    'logs': [],
                    'instrument': {'symbol': 'Error', 'exchange': 'Error', 'product': 'Error'},
                    'paperMode': self.paper_mode,
                    'lastUpdate': time.time()
                }), 500
        
        @self.app.route('/api/trades')
        def get_trades():
            """Get trade history"""
            try:
                return jsonify({
                    'trades': self.pos_mgr.get_trade_history(),
                    'stats': self.pos_mgr.get_session_stats() if self.paper_mode else {}
                })
            except Exception as e:
                self.logger.error(f"Error in /api/trades: {e}")
                self.logger.error(traceback.format_exc())
                return jsonify({
                    'trades': [],
                    'stats': {}
                }), 500
        
        @self.app.route('/api/export-trades')
        def export_trades():
            """Export trades to CSV"""
            try:
                filepath = self.pos_mgr.export_session_trades()
                if filepath:
                    return jsonify({
                        's': 'ok',
                        'message': f'Trades exported to {filepath}',
                        'filepath': filepath
                    })
                else:
                    return jsonify({
                        's': 'error',
                        'message': 'No trades to export'
                    })
            except Exception as e:
                self.logger.error(f"Error in /api/export-trades: {e}")
                self.logger.error(traceback.format_exc())
                return jsonify({
                    's': 'error',
                    'message': str(e)
                }), 500
        
        @self.app.errorhandler(404)
        def not_found(e):
            return jsonify({'error': 'Not found'}), 404
        
        @self.app.errorhandler(500)
        def internal_error(e):
            return jsonify({'error': 'Internal server error'}), 500
    
    def _get_state_data(self):
        """Get current state data"""
        try:
            data = {
                'instrument': {
                    'symbol': self.instrument.symbol,
                    'exchange': self.instrument.exchange,
                    'product': self.instrument.product
                },
                'position': self.pos_mgr.get_position(),
                'orderHistory': self.pos_mgr.get_order_history(),
                'logs': self.logger.get_entries(),
                'lastUpdate': time.time(),
                'paperMode': self.paper_mode
            }
            
            # Add paper trading specific data
            if self.paper_mode:
                data['sessionStats'] = self.pos_mgr.get_session_stats()
            
            return data
        except Exception as e:
            self.logger.error(f"Error building state data: {e}")
            self.logger.error(traceback.format_exc())
            raise
    
    def start(self, port=8080):
        """Start web server on specified port"""
        try:
            self.port = port
            self.logger.info(f"Web server starting on http://127.0.0.1:{port}")
            # Only bind to localhost for security
            self.app.run(host='127.0.0.1', port=int(port), debug=False, 
                        threaded=True, use_reloader=False)
        except Exception as e:
            self.logger.error(f"Error starting web server: {e}")
            self.logger.error(traceback.format_exc())
            raise
    
    def stop(self):
        """Stop web server (graceful shutdown)"""
        # Flask doesn't have a built-in stop method when run this way
        # Server will stop when main thread exits
        pass
    
    def broadcast_update(self):
        """Broadcast update to connected clients (no-op for REST API)"""
        pass
    
    def update_instrument(self, instrument):
        """Update instrument"""
        self.instrument = instrument
        self.logger.info(f"Web server: Instrument updated to {instrument.symbol}")