SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
GRID_SIZE = 30
GRID_MARGIN = 50
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
NEXT_PIECE_SIZE = 4

# 游戏模式常量
ENDLESS_MODE = 0
TIMED_MODE = 1
TWO_PLAYER_MODE = 2  # 添加双人模式常量
AI_MODE = 3  # 人机对战模式


# 游戏状态常量
LOGIN = -1
MENU = 0
RUNNING = 1
PAUSED = 2
GAME_OVER = 3
LEADERBOARD = 4  # 添加排行榜状态
HELP = "HELP"  # 添加帮助界面状态
ABOUT = "ABOUT"  # 添加关于界面状态

COLORS = {
    'I': (6, 182, 212),    # 蓝色
    'J': (37, 99, 235),    # 深蓝色
    'L': (249, 115, 22),   # 橙色
    'O': (234, 179, 8),    # 黄色
    'S': (16, 185, 129),   # 绿色
    'T': (139, 92, 246),   # 紫色
    'Z': (239, 68, 68),    # 红色
    'DARK': (31, 41, 55),      # 深色背景
    'LIGHT': (243, 244, 246),  # 浅色文本
    'ACCENT': (16, 185, 129),  # 强调色
    'SECONDARY': (236, 72, 153), # 次要色
    'PRIMARY': (79, 70, 229),    # 主色
    'WHITE': (255, 255, 255),
    'G': (128, 128, 128),  # 垃圾行的颜色设为灰色
}

SHAPES = {
    'I': [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
    'J': [[1, 0, 0], [1, 1, 1], [0, 0, 0]],
    'L': [[0, 0, 1], [1, 1, 1], [0, 0, 0]],
    'O': [[1, 1], [1, 1]],
    'S': [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
    'T': [[0, 1, 0], [1, 1, 1], [0, 0, 0]],
    'Z': [[1, 1, 0], [0, 1, 1], [0, 0, 0]]
}

# 限时模式时长(秒)
TIME_LIMIT = 180

# 添加网格显示设置（全局变量）
class GameSettings:
    SHOW_GRID = False  # 将SHOW_GRID改为类属性

# 创建全局设置实例
settings = GameSettings()

class Settings:
    def __init__(self):
        self.SHOW_GRID = False  # 默认关闭网格
        self.SOUND_ENABLED = False  # 默认关闭音效

settings = Settings()

# 添加道具配置
POWERUPS = {
    'bomb': {
        'name': '炸弹',
        'cost': 200,
        'description': '消除最下面一行',
        'icon_path': 'assets/images/bomb.png'
    },
    'lightning': {
        'name': '闪电',
        'cost': 1000,
        'description': '清除所有方块',
        'icon_path': 'assets/images/lightning.png'
    },
    'trash': {
        'name': '垃圾桶',
        'cost': 100,
        'description': '跳过当前方块',
        'icon_path': 'assets/images/trash.png'
    }
}
