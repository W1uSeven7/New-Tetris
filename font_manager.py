import pygame
import os
import platform

class FontManager:
    def __init__(self):
        self._default_font_path = self._get_system_font_path()
        
    def _get_system_font_path(self):
        """根据操作系统返回合适的字体路径"""
        system = platform.system()
        if system == 'Windows':
            # Windows 默认字体路径
            font_paths = [
                "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
                "C:/Windows/Fonts/simhei.ttf",  # 黑体
                "assets/fonts/msyh.ttc"  # 项目内置字体
            ]
            for path in font_paths:
                if os.path.exists(path):
                    return path
        elif system == 'Darwin':  # macOS
            return "/System/Library/Fonts/STHeiti Medium.ttc"
        
        # 如果找不到系统字体，使用项目内置字体
        return "assets/fonts/msyh.ttc"
    
    def get_font(self, size):
        """获取指定大小的字体"""
        try:
            return pygame.font.Font(self._default_font_path, size)
        except:
            # 如果加载失败，使用系统默认字体
            return pygame.font.SysFont('arial', size)