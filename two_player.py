from board import GameBoard
from player import HumanPlayer
import pygame
from config import settings  # 添加这行
from sound_manager import SoundManager  # 添加这行

class TwoPlayerGame:
    def __init__(self):
        """初始化双人游戏"""
        self.player1 = {
            'board': GameBoard(),
            'score': 0,
            'lines': 0,
            'is_game_over': False,
            'is_paused': False,  # 玩家1的暂停状态
        }
        self.player2 = {
            'board': GameBoard(),
            'score': 0,
            'lines': 0,
            'is_game_over': False,
            'is_paused': False,  # 玩家2的暂停状态
        }
        # 设置对手关系
        self.player1['board'].opponent = self.player2['board']
        self.player2['board'].opponent = self.player1['board']
        self._game_over = False
        self.is_paused = False  # 整体游戏的暂停状态
        self.clock = pygame.time.Clock()
        self.sound_manager = SoundManager()

    def toggle_pause(self):
        """切换整体游戏的暂停状态"""
        if not self._game_over:
            self.is_paused = not self.is_paused
            # 同步两个玩家的暂停状态
            self.player1['board'].is_paused = self.is_paused
            self.player2['board'].is_paused = self.is_paused

    def update(self):
        """更新游戏状态"""
        if not self.is_paused and not self._game_over:
            # 只有在游戏未暂停时更新游戏状态
            if not self.player1['is_paused']:
                self.player1['board'].update()
                self.player1['score'] = self.player1['board'].score
                self.player1['lines'] = self.player1['board'].lines
            
            if not self.player2['is_paused']:
                self.player2['board'].update()
                self.player2['score'] = self.player2['board'].score
                self.player2['lines'] = self.player2['board'].lines
            
            # 当任一方失败时，游戏立即结束
            if (self.player1['board'].is_game_over or 
                self.player2['board'].is_game_over):
                self._game_over = True

    def toggle_pause_player1(self):
        """切换玩家1的暂停状态"""
        if not self._game_over:
            self.player1['is_paused'] = not self.player1['is_paused']
            self.player1['board'].is_paused = self.player1['is_paused']

    def toggle_pause_player2(self):
        """切换玩家2的暂停状态"""
        if not self._game_over:
            self.player2['is_paused'] = not self.player2['is_paused']
            self.player2['board'].is_paused = self.player2['is_paused']

    def hard_drop_player1(self):
        """玩家1快速下落"""
        if not self._game_over and not self.player1['is_paused']:
            board = self.player1['board']
            if board.current_piece:
                board.hard_drop()

    def hard_drop_player2(self):
        """玩家2快速下落"""
        if not self._game_over and not self.player2['is_paused']:
            board = self.player2['board']
            if board.current_piece:
                board.hard_drop()

    @property
    def is_game_over(self):
        """获取游戏结束状态"""
        return self._game_over