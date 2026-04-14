import copy
from config import BOARD_WIDTH, BOARD_HEIGHT

# Dellacherie 权重配置
LH_WEIGHT = -0.6            # 越低高度越好，负权重
RE_WEIGHT = 0.8             # 消行奖励
RT_WEIGHT = -0.5           # 行变化率惩罚
CT_WEIGHT = -0.5            # 列变化率惩罚
NH_WEIGHT = -0.5            # 空洞惩罚
WS_WEIGHT = -0.5            # 井深惩罚

class AIPlayer:
    def __init__(self, board):
        self.board = board
        self.last_move_time = 0
        self.move_delay = 500
        self.next_move = None

    def get_best_move(self):
        piece = self.board.current_piece
        if not piece:
            return None

        best_score = float('-inf')
        best_move = None

        # 保存原始状态
        orig_x, orig_y, orig_rot = piece.x, piece.y, piece.rotation
        orig_shape = [row[:] for row in piece.shape]

        # 4 种旋转
        for rot in range(4):  # 最多4种旋转状态
            # 先恢复到初始状态
            piece.x, piece.y, piece.rotation = orig_x, orig_y, orig_rot
            piece.shape = [row[:] for row in orig_shape]
            
            # 旋转到目标状态
            current_rot = piece.rotation
            while current_rot != rot:
                self.board.rotate()
                if not self.board.is_valid(piece):
                    break
                current_rot = (current_rot + 1) % 4
                
            if current_rot != rot:  # 如果旋转失败，继续下一个
                continue
                
            shape = piece.shape
            w = len(shape[0])
            min_x = -2
            max_x = BOARD_WIDTH - w + 2
            
            for x in range(min_x, max_x):
                piece.x, piece.y = x, 0
                if not self.board.is_valid(piece):
                    continue
                    
                # 模拟下落
                while self.board.is_valid(piece, offset_row=1):
                    piece.y += 1
                    
                # 构建测试棋盘
                test_board = copy.deepcopy(self.board.board)
                for i in range(len(shape)):
                    for j in range(len(shape[i])):
                        if shape[i][j]:
                            yi, xj = piece.y + i, piece.x + j
                            if 0 <= yi < BOARD_HEIGHT and 0 <= xj < BOARD_WIDTH:
                                test_board[yi][xj] = 1
                                
                # 计算得分
                score = self.dellacherie_score(test_board, shape, piece.y)
                if score > best_score:
                    best_score = score
                    best_move = {'x': x, 'y': piece.y, 'rotation': rot}

        # 还原原始状态
        piece.x, piece.y, piece.rotation = orig_x, orig_y, orig_rot
        piece.shape = orig_shape
        
        return best_move

    def dellacherie_score(self, board_state, shape, drop_y):
        # 注意：RE 内需要行清和贡献块数，这里简单按清行数计
        lh = self.get_LH(board_state)
        re = self.get_RE(board_state)
        rt = self.get_RT(board_state)
        ct = self.get_CT(board_state)
        nh = self.get_NH(board_state)
        ws = self.get_WS(board_state)

        return (
            lh * LH_WEIGHT +
            re * RE_WEIGHT +
            rt * RT_WEIGHT +
            ct * CT_WEIGHT +
            nh * NH_WEIGHT +
            ws * WS_WEIGHT
        )

    def get_LH(self, board):
        # 最高块高度
        for row in range(BOARD_HEIGHT):
            if any(board[row][col] for col in range(BOARD_WIDTH)):
                return BOARD_HEIGHT - row
        return 0

    def get_RE(self, board):
        # 完整行数
        count = 0
        for row in board:
            if all(cell for cell in row):
                count += 1
        return count

    def get_RT(self, board):
        # 行变化率
        transitions = 0
        for i in range(BOARD_HEIGHT):
            last = 1
            for j in range(BOARD_WIDTH):
                curr = 1 if board[i][j] else 0
                if curr != last:
                    transitions += 1
                last = curr
            if last == 0:
                transitions += 1
        return transitions

    def get_CT(self, board):
        # 列变化率
        transitions = 0
        for j in range(BOARD_WIDTH):
            last = 1
            for i in range(BOARD_HEIGHT):
                curr = 1 if board[i][j] else 0
                if curr != last:
                    transitions += 1
                last = curr
            if last == 0:
                transitions += 1
        return transitions

    def get_NH(self, board):
        # 空洞数
        holes = 0
        for j in range(BOARD_WIDTH):
            block_found = False
            for i in range(BOARD_HEIGHT):
                if board[i][j]:
                    block_found = True
                elif block_found:
                    holes += 1
        return holes

    def get_WS(self, board):
        # 井深
        wells = 0
        for j in range(BOARD_WIDTH):
            for i in range(BOARD_HEIGHT):
                if board[i][j] == 0:
                    left = board[i][j-1] if j>0 else 1
                    right = board[i][j+1] if j<BOARD_WIDTH-1 else 1
                    if left and right:
                        k = i
                        while k < BOARD_HEIGHT and board[k][j] == 0:
                            wells += 1
                            k += 1
        return wells

    def make_move(self, current_time):
        from pygame import time
        if current_time - self.last_move_time < self.move_delay:
            return False
        self.last_move_time = current_time
        if not self.next_move:
            self.next_move = self.get_best_move()
        if not self.next_move:
            return False
        piece = self.board.current_piece
        # 旋转
        if piece.rotation != self.next_move['rotation']:
            target_rot = self.next_move['rotation']
            current_rot = piece.rotation
            # 计算最短旋转路径
            clockwise_steps = (target_rot - current_rot) % 4
            counter_clockwise_steps = (current_rot - target_rot) % 4
            
            # 选择最短的旋转方向
            if clockwise_steps <= counter_clockwise_steps:
                self.board.rotate()  # 顺时针旋转
            else:
                # 如果你的 Board 类支持逆时针旋转，可以使用逆时针旋转
                self.board.rotate()
            return True
        # 平移
        dx = self.next_move['x'] - piece.x
        if dx < 0:
            self.board.move('left')
            return True
        if dx > 0:
            self.board.move('right')
            return True
        # 硬降落
        self.board.hard_drop()
        self.next_move = None
        return True
