from config import (
    BOARD_WIDTH, BOARD_HEIGHT, COLORS, SHAPES,
    TIMED_MODE, ENDLESS_MODE, TIME_LIMIT,settings  # 添加ENDLESS_MODE
)
from sound_manager import SoundManager
import random
import pygame



class Piece:
    def __init__(self):
        """初始化方块"""
        self.type = random.choice(['I', 'O', 'T', 'S', 'Z', 'J', 'L'])  # 随机选择方块类型
        self.shape = SHAPES[self.type]
        self.color = self.type  # 设置颜色与类型相同
        self.x = BOARD_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0
        self.rotation = 0

    def set_shape(self, shape_type):
        """设置方块形状和颜色"""
        self.type = shape_type
        self.shape = SHAPES[shape_type]
        self.color = shape_type  # 确保颜色与类型同步

    def move(self, dx, dy):
        """移动方块"""
        self.x += dx
        self.y += dy

    def rotate(self):
        """旋转方块"""
        if not self.shape:
            return
        # 保存原始旋转状态
        original_rotation = self.rotation
        original_shape = self.shape
        # 尝试旋转
        self.rotation = (self.rotation + 1) % 4
        # 使用zip和切片进行矩阵旋转
        try:
            self.shape = list(list(x) for x in zip(*self.shape[::-1]))
        except Exception:
            # 如果旋转失败，还原原始状态
            self.rotation = original_rotation
            self.shape = original_shape

class GameBoard:
    def __init__(self, mode=ENDLESS_MODE):
        """初始化游戏板"""
        self.board = [[None for x in range(BOARD_WIDTH)] for y in range(BOARD_HEIGHT)]
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.lines = 0
        self.is_paused = False
        self.is_game_over = False
        self.mode = mode
        self.time_left = 180 if mode == TIMED_MODE else None
        self.last_time_update = pygame.time.get_ticks()
        self.clock = pygame.time.Clock()
        self.last_drop_time = pygame.time.get_ticks()
        self.speed = 1000
        self.base_speed = 1000
        self.piece_landed = False  # 添加方块落地标志
        self.sound_manager = SoundManager()  # 添加这行
        self.new_piece()  # 生成第一个方块
        self.lines_cleared = 0  # 初始化消除行数
        self.powerups = {
            'bomb': 0,
            'lightning': 0,
            'trash': 0
        }
        
    def new_piece(self):
        """生成新的当前方块"""
        if self.next_piece:
            self.current_piece = self.next_piece
        else:
            self.current_piece = self._create_new_piece()
        self.next_piece = self._create_new_piece()
        
        # print(1)    
        
        # 检查新方块是否可以放置
        if not self.is_valid(self.current_piece):
            self.is_game_over = True
    
    def _create_new_piece(self):
        """创建新方块"""
        shape_name = random.choice(list(SHAPES.keys()))
        piece = Piece()
        piece.set_shape(shape_name)  # 使用新方法设置形状和颜色
        return piece

    def rotate(self):
        """旋转当前方块"""
        if not self.current_piece or self.is_paused or self.is_game_over:
            return False
            
        # 保存原始形状以便还原
        original_shape = self.current_piece.shape
        
        # 尝试旋转
        self.current_piece.rotate()
        
        # 检查旋转后的位置是否有效
        if not self.is_valid(self.current_piece):
            # 如果无效则还原
            self.current_piece.shape = original_shape
            return False
        
        return True

    def is_valid(self, piece, offset_col=0, offset_row=0):
        """检查方块位置是否有效"""
        if not piece or not piece.shape:
            return False
            
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece.x + x + offset_col
                    new_y = piece.y + y + offset_row
                    
                    # 检查边界
                    if (new_x < 0 or 
                        new_x >= BOARD_WIDTH or 
                        new_y >= BOARD_HEIGHT or 
                        (new_y >= 0 and self.board[new_y][new_x])):
                        return False
        return True

    def lock_piece(self):
        """将当前方块固定到游戏板上"""
        if not self.current_piece:
            return
    
        # 将当前方块固定到板上
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    board_y = self.current_piece.y + y
                    board_x = self.current_piece.x + x
                    if 0 <= board_y < BOARD_HEIGHT and 0 <= board_x < BOARD_WIDTH:
                        self.board[board_y][board_x] = self.current_piece.color
    
        # 检查并清除完整行
        self.clear_lines()  # 只在这里调用一次
    
        # 生成新方块
        self.current_piece = self.next_piece
        self.next_piece = self._create_new_piece()
    
        # 检查游戏是否结束
        if not self.is_valid(self.current_piece):
            self.is_game_over = True
            self.current_piece = None

    def clear_lines(self):
        """清除完整的行并计算得分，但不清除垃圾行"""
        cleared_lines = []
    
        # 从下往上找出所有要消除的行
        for y in range(BOARD_HEIGHT - 1, -1, -1):
            # 检查是否为完整行，且不是垃圾行
            if all(self.board[y]) and not all(cell == 'G' for cell in self.board[y]):
                cleared_lines.append(y)
    
        cleared = len(cleared_lines)
        self.lines_cleared = cleared
    
        if cleared > 0:
            # 初始化音量变量
            current_volume = pygame.mixer.music.get_volume()
            
            # 保存原始状态和音量
            self.clear_animation_state = {
                'lines': cleared_lines,
                'flash_count': 3,
                'flash_state': True,
                'animation_done': False,
                'original_colors': {},
                'original_volume': current_volume
            }
            
            # 保存所有需要消除的行的原始颜色
            for line in cleared_lines:
                self.clear_animation_state['original_colors'][line] = self.board[line][:]
        
            # 计算得分
            score_map = {1: 100, 2: 300, 3: 600, 4: 1000}
            self.score += score_map.get(cleared, 1000)
            self.lines += cleared
            
            # 计算要发送的垃圾行数
            garbage_lines = 0
            if cleared >= 4:  # 消除4行发送4行
                garbage_lines = 4
            elif cleared == 3:  # 消除3行发送2行
                garbage_lines = 2
            elif cleared == 2:  # 消除2行发送1行
                garbage_lines = 1
            
            # 直接在这里处理垃圾行发送
            if garbage_lines > 0 and hasattr(self, 'opponent'):
                self.opponent.add_garbage_lines(garbage_lines)
                
            # # 移除非垃圾行
            # for line in cleared_lines:
            #     self.board.pop(line)
            #     # 在顶部添加新的空行
            #     self.board.insert(0, [None for _ in range(BOARD_WIDTH)])
        
            return cleared
        
        return 0

    def update_clear_animation(self):
        """更新消除动画"""
        if not hasattr(self, 'clear_animation_state') or not self.clear_animation_state:
            return False
        
        state = self.clear_animation_state
        
        # 闪烁动画
        if state['flash_count'] > 0:
            if state['flash_state']:
                # 变成白色
                for line in state['lines']:
                    for x in range(BOARD_WIDTH):
                        if self.board[line][x]:
                            self.board[line][x] = 'WHITE'
            else:
                # 恢复原色
                for line in state['lines']:
                    for x in range(BOARD_WIDTH):
                        if self.board[line][x]:
                            self.board[line][x] = state['original_colors'][line][x]
                state['flash_count'] -= 1
        
            state['flash_state'] = not state['flash_state']
            return True
        
        # 闪烁结束后执行消除
        if not state['animation_done']:
            # 创建新的游戏板
            new_board = [['' for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
            write_line = BOARD_HEIGHT - 1
            
            # 从下往上遍历，跳过要消除的行
            for read_line in range(BOARD_HEIGHT - 1, -1, -1):
                if read_line not in state['lines']:
                    new_board[write_line] = self.board[read_line][:]
                    write_line -= 1
            
            # 更新游戏板
            self.board = new_board
            
            # 恢复背景音乐音量
            if settings.SOUND_ENABLED:
                pygame.mixer.music.set_volume(state['original_volume'])
            
            # 完成动画
            state['animation_done'] = True
            self.clear_animation_state = None
    
        return False

    def drop(self):
        if self.is_valid(self.current_piece, offset_row=1):
            self.current_piece.y += 1
        else:
            self.lock_piece()

    def hard_drop(self):
        """快速下落当前方块"""
        if not self.current_piece or self.is_paused or self.is_game_over:
            return False
            
        # 保存原始位置
        original_y = self.current_piece.y
        
        # 找到最低可落位置
        while self.is_valid(self.current_piece, offset_row=1):
            self.current_piece.y += 1
        
        # 只有在方块真的下落了的情况下才锁定并生成新方块
        if self.current_piece.y > original_y:
            self.piece_landed = True
            # 硬降落时播放音效
            if settings.SOUND_ENABLED:
                self.sound_manager.play_sound('drop')
            self.lock_piece()
            # self.clear_lines()
            return True
        return False

    def move(self, direction):
        """移动当前方块"""
        if not self.current_piece or self.is_paused or self.is_game_over:
            return False
            
        if direction == 'left':
            if self.is_valid(self.current_piece, offset_col=-1):
                self.current_piece.move(-1, 0)
                return True
        elif direction == 'right':
            if self.is_valid(self.current_piece, offset_col=1):
                self.current_piece.move(1, 0)
                return True
        elif direction == 'down':
            if self.is_valid(self.current_piece, offset_row=1):
                self.current_piece.move(0, 1)
                return True
            else:
                self.piece_landed = True  # 设置方块落地标志
                self.lock_piece()  # 这里只调用 lock_piece，不需要再调用 clear_lines
        return False

    def update(self):
        """更新游戏状态"""
        if self.is_paused or self.is_game_over:
            return

        # 更新消除动画
        if hasattr(self, 'clear_animation_state') and self.clear_animation_state:
            if self.update_clear_animation():
                return  # 如果动画还在进行，不执行其他更新

        now = pygame.time.get_ticks()
        
        # 更新限时模式的时间
        if self.mode == TIMED_MODE and self.time_left is not None:
            time_passed = (now - self.last_time_update) / 1000.0  # 转换为秒
            self.time_left = max(0, self.time_left - time_passed)
            self.last_time_update = now
            
            # 时间用完，游戏结束
            if self.time_left <= 0:
                self.is_game_over = True
                return

        # 方块下落逻辑
        if now - self.last_drop_time > self.speed:
            if self.current_piece:
                if self.is_valid(self.current_piece, offset_row=1):
                    self.current_piece.move(0, 1)
                else:
                    self.lock_piece()
                    # self.clear_lines()
                    # self.new_piece()
                    if not self.is_valid(self.current_piece):
                        self.is_game_over = True
            self.last_drop_time = now
    
    def can_buy_powerup(self, powerup_type):
        """检查是否可以购买道具"""
        costs = {
            'bomb': 200,
            'lightning': 1000,
            'trash': 100
        }
        return self.score >= costs[powerup_type]
        
    def use_bomb(self):
        """使用炸弹道具，清除最下面一行并让上面的行下落"""
        if self.score < 200:
            return False
            
        # 从底部开始查找第一个非空行
        found_non_empty = False
        for y in range(BOARD_HEIGHT-1, -1, -1):
            if any(self.board[y]):
                found_non_empty = True
                # 只移动这一行以上的内容
                for move_y in range(y, 0, -1):
                    self.board[move_y] = self.board[move_y-1][:]
                # 最上面一行设为空
                self.board[0] = [None for _ in range(BOARD_WIDTH)]
                # 扣除分数
                self.score -= 200
                return True
            
        return False  # 如果没有找到非空行
    
    def use_lightning(self):
        """使用闪电道具，清除所有方块"""
        # 检查分数是否足够
        if self.score < 1000:
            return False
            
        # 检查是否有方块可以清除
        has_blocks = False
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.board[y][x] is not None:
                    has_blocks = True
                    break
            if has_blocks:
                break
                
        if has_blocks:
            # 清除所有方块
            self.board = [[None for x in range(BOARD_WIDTH)] for y in range(BOARD_HEIGHT)]
            # 扣除分数
            self.score -= 1000
            return True
            
        return False  # 如果没有方块可以清除
    
    def use_trash(self):
        """使用垃圾桶道具，跳过当前方块"""
        # 检查分数是否足够
        if self.score < 100:
            return False
            
        # 检查是否有正在下落的方块
        if not self.current_piece:
            return False
            
        # 直接切换到下一个方块
        self.current_piece = self.next_piece
        self.next_piece = self._create_new_piece()
        
        # 扣除分数
        self.score -= 100
        return True
    
    def add_garbage_lines(self, num_lines):
        """添加垃圾行，添加满行且不可消除的灰色行"""
        if num_lines <= 0:
            return
        
        # 将现有方块向上移动num_lines行
        for y in range(num_lines):
            self.board.pop(0)  # 移除顶部行
            
        # 从底部开始添加垃圾行
        for i in range(num_lines):
            # 创建新的垃圾行：全部填充灰色且不可消除的方块
            new_line = ['G' for _ in range(BOARD_WIDTH)]  # 'G' 表示不可消除的垃圾行方块
            self.board.append(new_line)  # 在底部添加新行