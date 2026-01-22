"""
Web server for dashboard with Paper Trading support
"""
import json
import os
import threading
import time
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
        CORS(self.app)
        self.ws_clients = []
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def home():
            # Use absolute path from project root
            html_path = self.project_root / 'web' / 'index.html'
            if not html_path.exists():
                return f"Error: index.html not found at {html_path}", 404
            return send_file(str(html_path))
        
        @self.app.route('/api/state')
        def get_state():
            return jsonify(self._get_state_data())
        
        @self.app.route('/api/trades')
        def get_trades():
            """Get trade history"""
            return jsonify({
                'trades': self.pos_mgr.get_trade_history(),
                'stats': self.pos_mgr.get_session_stats() if self.paper_mode else {}
            })
        
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
                return jsonify({
                    's': 'error',
                    'message': str(e)
                })
    
    def _get_state_data(self):
        """Get current state data"""
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
    
    def start(self, port=8080):
        """Start web server on specified port"""
        self.port = port
        self.logger.info(f"Web server starting on port {port}")
        # Only bind to localhost for security
        self.app.run(host='127.0.0.1', port=int(port), debug=False, 
                    threaded=True, use_reloader=False)
    
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