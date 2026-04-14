import pygame
from two_player import TwoPlayerGame
from ai_player import AIPlayer

class AIGame(TwoPlayerGame):
    def __init__(self):
        super().__init__()  # 初始化双人游戏基类
        self.ai_player = AIPlayer(self.player1['board'])  # AI控制左侧玩家
        
    def update(self):
        """更新游戏状态"""
        if not self.is_paused and not self.is_game_over:
            # AI移动
            if not self.player1['board'].is_paused:
                self.ai_player.make_move(pygame.time.get_ticks())
            
            # 更新游戏状态
            super().update()

