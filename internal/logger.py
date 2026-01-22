"""
Logging system for trading application
"""

import threading
from datetime import datetime
from typing import List, Dict


class LogEntry:
    """Single log entry"""

    def __init__(self, timestamp: datetime, level: str, message: str):
        self.timestamp = timestamp
        self.level = level
        self.message = message

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'message': self.message
        }


class Logger:
    """Thread-safe logger with in-memory storage"""

    def __init__(self, filename: str, max_entries: int = 1000):
        self.filename = filename
        self.max_entries = max_entries
        self.entries: List[LogEntry] = []
        self.lock = threading.Lock()

        # Open file handle
        try:
            self.file = open(filename, 'a')
        except Exception as e:
            print(f"Warning: Could not open log file {filename}: {e}")
            self.file = None

    def _log(self, level: str, message: str):
        """Internal log method"""
        timestamp = datetime.now()
        entry = LogEntry(timestamp, level, message)

        with self.lock:
            # Add to in-memory storage
            self.entries.append(entry)
            if len(self.entries) > self.max_entries:
                self.entries.pop(0)

            # Write to file
            if self.file:
                log_line = f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {message}\n"
                self.file.write(log_line)
                self.file.flush()

    def debug(self, message: str):
        """Log debug message"""
        self._log("DEBUG", message)

    def info(self, message: str):
        """Log info message"""
        self._log("INFO", message)

    def warn(self, message: str):
        """Log warning message"""
        self._log("WARN", message)

    def error(self, message: str):
        """Log error message"""
        self._log("ERROR", message)

    def get_entries(self) -> List[Dict]:
        """Get all log entries"""
        with self.lock:
            return [entry.to_dict() for entry in self.entries]

    def close(self):
        """Close file handle"""
        if self.file:
            self.file.close()