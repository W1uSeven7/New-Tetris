class HumanPlayer:
    def __init__(self, gameboard):
        self.gameboard = gameboard

    def handle_key(self, key):
        if key == 'left':
            self.gameboard.move('left')
        elif key == 'right':
            self.gameboard.move('right')
        elif key == 'down':
            self.gameboard.move('down')
        elif key == 'rotate':
            self.gameboard.rotate()
        elif key == 'hard_drop':
            self.gameboard.hard_drop()
        elif key == 'pause':
            self.gameboard.is_paused = not self.gameboard.is_paused
