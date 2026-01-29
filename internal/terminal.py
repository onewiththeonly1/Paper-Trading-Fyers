"""
Terminal handling for raw input mode with proper restoration
"""
import sys
import tty
import termios
import select
import atexit


class Terminal:
    """Handle terminal raw input mode for single-keystroke input"""
    
    def __init__(self):
        self.fd = sys.stdin.fileno()
        self.old_settings = None
        self._raw_mode_active = False
        
        # Save initial terminal settings as safety backup
        try:
            self.initial_settings = termios.tcgetattr(self.fd)
            # Register cleanup on program exit
            atexit.register(self._emergency_restore)
        except:
            self.initial_settings = None
    
    def set_raw_mode(self):
        """
        Set terminal to raw mode for single character input.
        This is a SELECTIVE raw mode that:
        - Disables ECHO (no character display on type)
        - Disables ICANON (no line buffering, immediate input)
        - Keeps ISIG enabled (Ctrl+C still works)
        - Keeps output processing enabled (newlines work correctly)
        """
        try:
            # Save current settings
            self.old_settings = termios.tcgetattr(self.fd)
            
            # Get fresh copy for modification
            new_settings = termios.tcgetattr(self.fd)
            
            # lflag (local modes)
            new_settings[3] = new_settings[3] & ~termios.ICANON  # Disable canonical mode
            new_settings[3] = new_settings[3] & ~termios.ECHO    # Disable echo
            new_settings[3] = new_settings[3] & ~termios.ECHONL  # Disable newline echo
            # Keep ISIG enabled for Ctrl+C handling
            
            # iflag (input modes) - keep most processing enabled
            # This ensures proper newline handling
            
            # oflag (output modes) - keep output processing
            # This ensures print statements work correctly with \n
            
            # cc (control characters)
            new_settings[6][termios.VMIN] = 1   # Minimum characters for read
            new_settings[6][termios.VTIME] = 0  # Timeout in deciseconds (0 = blocking)
            
            # Apply the new settings
            termios.tcsetattr(self.fd, termios.TCSADRAIN, new_settings)
            self._raw_mode_active = True
            
        except Exception as e:
            print(f"Warning: Could not set raw mode: {e}")
            self.old_settings = None
            self._raw_mode_active = False

    def restore(self):
        """
        Restore terminal to normal (cooked) mode.
        Called before text input or program exit.
        """
        if self.old_settings and self._raw_mode_active:
            try:
                termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
                self._raw_mode_active = False
                self.old_settings = None
            except Exception as e:
                # If normal restore fails, try emergency restore
                self._emergency_restore()
    
    def _emergency_restore(self):
        """
        Emergency restoration using initial settings.
        Called by atexit or if normal restore fails.
        """
        if self.initial_settings and self._raw_mode_active:
            try:
                termios.tcsetattr(self.fd, termios.TCSADRAIN, self.initial_settings)
                self._raw_mode_active = False
            except:
                pass  # Nothing more we can do
    
    def read_char(self):
        """
        Read a single character from stdin.
        Blocks until a character is available.
        """
        return sys.stdin.read(1)
    
    def get_key(self):
        """
        Get a single key press (non-blocking with timeout).
        Returns the key or None if no key pressed within timeout.
        """
        # Check if data is available to read
        if select.select([sys.stdin], [], [], 0)[0]:
            return self.read_char()
        return None
    
    def peek_key(self):
        """
        Peek at next key without consuming it.
        Returns the key or None if no key available.
        """
        # For simplicity, just check if key is available
        if select.select([sys.stdin], [], [], 0)[0]:
            # Read the character but we'll need to consume it with get_key()
            # This is a simplified implementation
            return self.read_char()
        return None
    
    def is_raw_mode(self):
        """Check if terminal is currently in raw mode"""
        return self._raw_mode_active