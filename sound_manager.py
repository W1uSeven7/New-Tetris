import pygame

class SoundManager:
    def __init__(self):
        self.enabled = False  # 默认关闭音效
        
        # 加载音效
        self.sounds = {
            'click': pygame.mixer.Sound('assets/sounds/click.mp3'),    # 点击音效
            'clear_1': pygame.mixer.Sound('assets/sounds/clear_1.mp3'), # 消除一行的音效
            'clear_2': pygame.mixer.Sound('assets/sounds/clear_2.mp3'),  # 消除两行的音效
            'clear_3': pygame.mixer.Sound('assets/sounds/clear_3.mp3'),  # 消除三行以上的音效
            'game_over': pygame.mixer.Sound('assets/sounds/game_over.mp3'), # 游戏结束音效
            'rotate': pygame.mixer.Sound('assets/sounds/rotate.mp3'),  # 方块旋转音效
            'drop': pygame.mixer.Sound('assets/sounds/drop.mp3'),     # 方块固定音效
            'tool_1': pygame.mixer.Sound('assets/sounds/tool_1.mp3'),     # 方块固定音效
            'tool_2': pygame.mixer.Sound('assets/sounds/tool_2.mp3'),     # 方块固定音效
            'tool_3': pygame.mixer.Sound('assets/sounds/tool_3.mp3')     # 方块固定音效
        }
        
        # 加载背景音乐
        self.bgm_file = 'assets/sounds/bgm.mp3'
        
        # 设置音量
        self.bgm_volume = 0.09
        self.sfx_volume = 0.1
        
        # 为不同类型的音效设置不同音量
        self.volume_settings = {
            'click': 0.5,      # 点击音效适中
            'clear_1': 0.5,    # 消除音效较大
            'clear_2': 0.6,    # 双消音效更大
            'clear_3': 0.8,    # 三消及以上音效最大
            'game_over': 0.3,   # 游戏结束音效较大
            'rotate': 0.5,     # 旋转音效适中
            'drop': 0.5,       # 放置音效适中
            'tool_1': 0.7,       # 放置音效适中
            'tool_2': 0.7,       # 放置音效适中
            'tool_3': 0.7,       # 放置音效适中
        }
        
        # 初始化各音效的音量
        for sound_name, sound in self.sounds.items():
            volume = self.volume_settings.get(sound_name, 0)
            sound.set_volume(volume)
            
    def toggle_sound(self):
        """切换音效开关"""
        self.enabled = not self.enabled
    
        # 设置背景音乐音量
        if self.enabled:
            pygame.mixer.music.set_volume(self.bgm_volume)
        else:
            pygame.mixer.music.set_volume(0)
        
        # 设置所有音效的音量
        for sound_name, sound in self.sounds.items():
            if self.enabled:
                # 启用时使用预设的音量
                volume = self.volume_settings.get(sound_name, 0.5)
            else:
                # 禁用时设置为0
                volume = 0
            sound.set_volume(volume)
    
    def play_bgm(self):
        """播放背景音乐"""
        pygame.mixer.music.load(self.bgm_file)
        pygame.mixer.music.set_volume(0 if not self.enabled else self.bgm_volume)
        pygame.mixer.music.play(-1)  # -1表示循环播放
            
    def play_sound(self, sound_name):
        """播放指定音效"""
        if self.enabled and sound_name in self.sounds:
            self.sounds[sound_name].play()