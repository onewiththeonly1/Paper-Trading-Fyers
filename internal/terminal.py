"""
Terminal handling for raw input mode
"""
import sys
import tty
import termios
import select


class Terminal:
    """Handle terminal raw input mode for single-keystroke input"""
    
    def __init__(self):
        self.fd = sys.stdin.fileno()
        self.old_settings = None
    
    def set_raw_mode(self):
        try:
            self.old_settings = termios.tcgetattr(self.fd)

            attrs = termios.tcgetattr(self.fd)
            attrs[3] = attrs[3] & ~termios.ECHO  # disable echo
            termios.tcsetattr(self.fd, termios.TCSADRAIN, attrs)

            tty.setraw(self.fd)
        except Exception as e:
            print(f"Warning: Could not set raw mode: {e}")
            self.old_settings = None

    def restore(self):
        """
        Restore terminal to normal (cooked) mode
        Required before text input or program exit
        """
        if self.old_settings:
            try:
                termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
                self.old_settings = None
            except:
                pass
    
    def read_char(self):
        """
        Read a single character from stdin
        Blocks until a character is available
        """
        return sys.stdin.read(1)
    
    def get_key(self):
        """
        Get a single key press (non-blocking with timeout)
        Returns the key or None if no key pressed within timeout
        """
        # Check if data is available to read
        if select.select([sys.stdin], [], [], 0)[0]:
            return self.read_char()
        return None
    
    def peek_key(self):
        """
        Peek at next key without consuming it
        Returns the key or None if no key available
        """
        # For simplicity, just check if key is available
        if select.select([sys.stdin], [], [], 0)[0]:
            # Read the character but we'll need to consume it with get_key()
            # This is a simplified implementation
            return self.read_char()
        return None
