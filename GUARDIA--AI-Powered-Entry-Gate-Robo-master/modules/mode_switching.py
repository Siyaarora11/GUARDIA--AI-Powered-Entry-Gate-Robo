# modules/mode_switching.py

class ModeSwitching:
    def __init__(self):
        self.current_mode = 'security'

    def switch_mode(self, mode):
        if mode in ['security', 'assistant']:
            self.current_mode = mode
            print(f"Switched to {mode} mode")
            return True
        else:
            print("Invalid mode")
            return False
