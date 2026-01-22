"""
Configuration management for Fyers trading app
"""

import json
from typing import List


class InstrumentConfig:
    """Configuration for a trading instrument"""

    def __init__(self, symbol: str, exchange: str, lot_size: int, product: str = "INTRADAY"):
        self.symbol = symbol
        self.exchange = exchange
        self.lot_size = lot_size
        self.product = product or "INTRADAY"

    @classmethod
    def from_dict(cls, data: dict):
        """Create InstrumentConfig from dictionary"""
        return cls(
            symbol=data['symbol'],
            exchange=data['exchange'],
            lot_size=data['lot_size'],
            product=data.get('product', 'INTRADAY')
        )


class Config:
    """Main configuration class"""

    def __init__(self, app_id: str, app_secret: str, redirect_uri: str,
                 access_token: str, instruments: List[InstrumentConfig]):
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
        self.access_token = access_token
        self.instruments = instruments

    @classmethod
    def load(cls, filename: str):
        """Load configuration from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise Exception(f"Configuration file {filename} not found")
        except json.JSONDecodeError as e:
            raise Exception(f"Error decoding {filename}: {e}")

        # Validate required fields
        if not data.get('app_id'):
            raise Exception("app_id is required in config.json")
        if not data.get('access_token'):
            raise Exception("access_token is required in config.json. Run: python generate_token.py")
        if not data.get('instruments') or len(data['instruments']) == 0:
            raise Exception("At least one instrument is required in config.json")

        # Parse instruments
        instruments = []
        for i, inst_data in enumerate(data['instruments']):
            if not inst_data.get('symbol'):
                raise Exception(f"Instrument {i+1}: symbol is required")
            if not inst_data.get('exchange'):
                raise Exception(f"Instrument {i+1}: exchange is required")
            if not inst_data.get('lot_size') or inst_data['lot_size'] <= 0:
                raise Exception(f"Instrument {i+1}: lot_size must be greater than 0")

            instruments.append(InstrumentConfig.from_dict(inst_data))

        return cls(
            app_id=data['app_id'],
            app_secret=data.get('app_secret', ''),
            redirect_uri=data.get('redirect_uri', ''),
            access_token=data['access_token'],
            instruments=instruments
        )