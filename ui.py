from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, GRID_MARGIN, 
    BOARD_WIDTH, BOARD_HEIGHT, NEXT_PIECE_SIZE, COLORS, SHAPES,
    TIMED_MODE, ENDLESS_MODE, TWO_PLAYER_MODE,
    settings, POWERUPS, MENU  # 导入settings实例而不是SHOW_GRID
)

import pygame
import random
import math
from ai_game import AIGame  
from two_player import TwoPlayerGame
from font_manager import FontManager

font_manager = FontManager()

# 菜单装饰方块（所有界面共用）
menu_decor_blocks = None

# 加载设置图标图片
SETTINGS_ICON = pygame.image.load('assets/images/image.png')
# 调整图标大小为40x40像素
SETTINGS_ICON = pygame.transform.scale(SETTINGS_ICON, (40, 40))

def generate_menu_decor_blocks():
    """
    生成两侧的装饰方块
    固定位置,随机变换形状
    """
    blocks = []
    piece_types = list(SHAPES.keys())
    
    # 为左右两侧各生成装饰方块
    positions = [
        # 左侧位置 [(x, y), ...]
        [(50, 200), (50, 350), (50, 500), (50, 650)],
        # 右侧位置 [(x, y), ...] - 将x坐标增加到更靠右的位置
        [(SCREEN_WIDTH-90, 200), (SCREEN_WIDTH-90, 350), 
         (SCREEN_WIDTH-90, 500), (SCREEN_WIDTH-90, 650)]
    ]
    
    for side_positions in positions:
        side_blocks = []
        for x, y in side_positions:
            piece_type = random.choice(piece_types)
            block = {
                'type': piece_type,
                'shape': SHAPES[piece_type],
                'color': COLORS[piece_type],
                'x': x,
                'y': y
            }
            side_blocks.append(block)
        blocks.append(side_blocks)
    return blocks

def update_menu_decor_blocks():
    """
    更新装饰方块:随机改变形状
    """
    global menu_decor_blocks
    
    if menu_decor_blocks is None:
        menu_decor_blocks = generate_menu_decor_blocks()
        return
        
    piece_types = list(SHAPES.keys())
    for side_blocks in menu_decor_blocks:
        for block in side_blocks:
            # 随机更新方块类型
            new_type = random.choice(piece_types)
            block['type'] = new_type
            block['shape'] = SHAPES[new_type]
            block['color'] = COLORS[new_type]

def draw_tetris_piece(screen, shape, x, y, color, size=GRID_SIZE//2):
    """
    绘制一个完整的俄罗斯方块
    """
    for row in range(len(shape)):
        for col in range(len(shape[row])):
            if shape[row][col]:
                block_rect = pygame.Rect(
                    x + col * size, 
                    y + row * size, 
                    size, 
                    size
                )
                pygame.draw.rect(screen, color, block_rect)
                pygame.draw.rect(screen, COLORS['LIGHT'], block_rect, 1)

def draw_menu_decor(screen):
    """
    绘制菜单装饰方块
    """
    if menu_decor_blocks:
        for side_blocks in menu_decor_blocks:
            for block in side_blocks:
                draw_tetris_piece(
                    screen,
                    block['shape'],
                    block['x'],
                    block['y'],
                    block['color']
                )

def draw_board(screen, board, current_piece, offset_x=GRID_MARGIN, offset_y=GRID_MARGIN):
    """绘制游戏板"""
    # 向左偏移游戏主体
    left = offset_x + 0
    top = offset_y
    
    # 绘制边框
    board_rect = pygame.Rect(
        left - 2, 
        top - 2,
        BOARD_WIDTH * GRID_SIZE + 4,
        BOARD_HEIGHT * GRID_SIZE + 4
    )
    pygame.draw.rect(screen, COLORS['LIGHT'], board_rect, 2)

    # 如果启用了网格，绘制网格线
    if settings.SHOW_GRID:
        for x in range(BOARD_WIDTH + 1):
            pygame.draw.line(screen, COLORS['PRIMARY'],
                           (offset_x + x * GRID_SIZE, offset_y),
                           (offset_x + x * GRID_SIZE, offset_y + BOARD_HEIGHT * GRID_SIZE))
        for y in range(BOARD_HEIGHT + 1):
            pygame.draw.line(screen, COLORS['PRIMARY'],
                           (offset_x, offset_y + y * GRID_SIZE),
                           (offset_x + BOARD_WIDTH * GRID_SIZE, offset_y + y * GRID_SIZE))
    
    
    # 绘制已固定的方块
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if cell:
                block_rect = pygame.Rect(
                    left + x * GRID_SIZE,
                    top + y * GRID_SIZE,
                    GRID_SIZE - 1,
                    GRID_SIZE - 1
                )
                pygame.draw.rect(screen, COLORS[cell], block_rect)
    
    # 绘制当前方块
    if current_piece:
        for y, row in enumerate(current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    block_rect = pygame.Rect(
                        left + (current_piece.x + x) * GRID_SIZE,
                        top + (current_piece.y + y) * GRID_SIZE,
                        GRID_SIZE - 1,
                        GRID_SIZE - 1
                    )
                    pygame.draw.rect(screen, COLORS[current_piece.color], block_rect)

    # 在单人模式下显示道具按钮
    if not isinstance(board, TwoPlayerGame):
        powerup_rects = draw_powerup_buttons(screen, font_manager.get_font(20))
        return powerup_rects

def draw_side_panel(screen, small_font, game, is_paused, is_game_over, offset_x=0, player_name="玩家"):
    """绘制侧边面板"""
    panel_x = GRID_MARGIN + BOARD_WIDTH * GRID_SIZE + 20 + offset_x
    next_y = GRID_MARGIN
    
    # 绘制下一个方块标题
    title = small_font.render(f"下一个方块", True, COLORS['ACCENT'])
    screen.blit(title, (panel_x, next_y))
    
    # 绘制预览区域背景
    preview_size = NEXT_PIECE_SIZE * GRID_SIZE
    preview_rect = pygame.Rect(panel_x, next_y + 30, preview_size, preview_size)
    pygame.draw.rect(screen, COLORS['DARK'], preview_rect)
    
    # 绘制下一个方块
    if game.next_piece:
        # 计算方块形状的尺寸
        shape = game.next_piece.shape
        shape_height = len(shape)
        shape_width = len(shape[0])
        
        # print(f"Next piece shape: {game.next_piece.type}")
        
        # 计算居中偏移
        offset_x = (preview_size - shape_width * GRID_SIZE) // 2
        offset_y = (preview_size - shape_height * GRID_SIZE) // 2
        
        # 绘制方块
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    block_x = panel_x + offset_x + x * GRID_SIZE
                    block_y = next_y + 30 + offset_y + y * GRID_SIZE
                    block_rect = pygame.Rect(block_x, block_y, GRID_SIZE - 2, GRID_SIZE - 2)
                    pygame.draw.rect(screen, COLORS[game.next_piece.color], block_rect)
    
    # 添加限时模式倒计时显示
    if game.mode == TIMED_MODE and hasattr(game, 'time_left'):
        time_text = small_font.render(f"剩余时间: {int(game.time_left)}秒", True, COLORS['ACCENT'])
        screen.blit(time_text, (panel_x, next_y + 280))

    score_text = small_font.render(f"得分: {game.score}", True, COLORS['LIGHT'])
    lines_text = small_font.render(f"行数: {game.lines}", True, COLORS['LIGHT'])
    screen.blit(score_text, (panel_x, next_y + 200))
    screen.blit(lines_text, (panel_x, next_y + 240))

    # 添加暂停和直接落下按钮
    btn_width, btn_height = 120, 40
    pause_btn = pygame.Rect(panel_x, next_y + 320, btn_width, btn_height)
    drop_btn = pygame.Rect(panel_x, next_y + 380, btn_width, btn_height)
    
    # 绘制按钮
    pygame.draw.rect(screen, COLORS['PRIMARY'] if not is_paused else COLORS['SECONDARY'], pause_btn)
    pygame.draw.rect(screen, COLORS['PRIMARY'], drop_btn)
    
    # 绘制按钮文本
    pause_text = small_font.render("继续" if is_paused else "暂停", True, COLORS['LIGHT'])
    drop_text = small_font.render("直接落下", True, COLORS['LIGHT'])
    
    screen.blit(pause_text, (pause_btn.centerx - pause_text.get_width()//2, pause_btn.y + 10))
    screen.blit(drop_text, (drop_btn.centerx - drop_text.get_width()//2, drop_btn.y + 10))
    
    # 返回格式与双人模式保持一致
    return ((pause_btn, drop_btn), None)

def draw_game_over(screen, font, small_font, is_game_over, game, db, current_user):
    """
    绘制游戏结束界面，包含历史最高分
    """
    if not is_game_over:
        return None, None
        
    # 半透明黑色背景
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(180)
    screen.blit(overlay, (0, 0))
    
    # 游戏结束标题
    game_over_text = font.render("游戏结束", True, COLORS['ACCENT'])
    text_rect = game_over_text.get_rect(centerx=SCREEN_WIDTH//2, centery=230)
    screen.blit(game_over_text, text_rect)
    
    # 本局得分
    score_text = small_font.render(f"本局得分: {game.score}", True, COLORS['LIGHT'])
    screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 300))
    
    lines_text = small_font.render(f"消除行数: {game.lines}", True, COLORS['LIGHT'])
    screen.blit(lines_text, (SCREEN_WIDTH//2 - lines_text.get_width()//2, 330))
    
    # 显示历史最高分
    if current_user:
        mode_str = 'endless' if game.mode == ENDLESS_MODE else 'timed'
        high_scores = db.get_high_scores(mode=mode_str, user_id=current_user, limit=1)
        if high_scores:
            high_score = high_scores[0][1]  # (username, score, lines)
            high_score_text = small_font.render(f"历史最高分: {high_score}", True, COLORS['ACCENT'])
            screen.blit(high_score_text, (SCREEN_WIDTH//2 - high_score_text.get_width()//2, 380))
    
    # 添加按钮
    btn_width, btn_height = 200, 50
    btn_y = 450
    spacing = 20
    
    # 重新开始按钮
    restart_btn = pygame.Rect(
        SCREEN_WIDTH//2 - btn_width - spacing//2,
        btn_y,
        btn_width,
        btn_height
    )
    pygame.draw.rect(screen, COLORS['PRIMARY'], restart_btn, border_radius=8)
    restart_text = small_font.render("重新开始 (R)", True, COLORS['LIGHT'])
    text_rect = restart_text.get_rect(center=restart_btn.center)
    screen.blit(restart_text, text_rect)
    
    # 返回菜单按钮
    menu_btn = pygame.Rect(
        SCREEN_WIDTH//2 + spacing//2,
        btn_y,
        btn_width,
        btn_height
    )
    pygame.draw.rect(screen, COLORS['PRIMARY'], menu_btn, border_radius=8)
    menu_text = small_font.render("返回菜单 (M)", True, COLORS['LIGHT'])
    text_rect = menu_text.get_rect(center=menu_btn.center)
    screen.blit(menu_text, text_rect)
    
    return restart_btn, menu_btn

def draw_start_menu(screen, font, small_font, draw_buttons=True):
    """绘制开始菜单界面"""
    # 绘制主标题
    title = font.render("俄罗斯方块", True, COLORS['ACCENT'])
    title_rect = title.get_rect(centerx=SCREEN_WIDTH//2, top=70)  # 稍微上移主标题
    screen.blit(title, title_rect)
    
    
    # 添加小标题
    title_font = font_manager.get_font(30)
    subtitle = title_font.render("TetraNova: 重构方块世界", True, COLORS['LIGHT'])
    subtitle_rect = subtitle.get_rect(centerx=SCREEN_WIDTH//2, top=title_rect.bottom + 20)
    screen.blit(subtitle, subtitle_rect)
    
    # 绘制装饰方块
    draw_menu_decor(screen)
    btn_y = 220  # 增加这个值以适应新添加的小标题
    btn_height = 60
    btn_width = 200
    btn_spacing = 40
    text_surface = None
    text_rect = None

    
    btn_rects = []
    if True:
        
        buttons = ["无尽模式", "限时模式", "双人模式", "人机模式", "排行榜"]


        for i, text in enumerate(buttons):
            btn_rect = pygame.Rect(
                SCREEN_WIDTH//2 - btn_width//2,
                btn_y + i * (btn_height + btn_spacing),
                btn_width,
                btn_height
            )

            if draw_buttons:
                pygame.draw.rect(screen, COLORS['PRIMARY'], btn_rect, border_radius=10)
                
                text_surface = small_font.render(text, True, COLORS['LIGHT'])
                text_rect = text_surface.get_rect(center=btn_rect.center)
                screen.blit(text_surface, text_rect)
                
                btn_rects.append(btn_rect)
        
        # 添加小按钮
        small_btn_y = btn_y + (len(buttons) * (btn_height + btn_spacing))  + 40 # 在最后一个主按钮下方留出空间
        small_btn_width = 100  # 小按钮宽度
        small_btn_height = 30  # 小按钮高度
        small_btn_spacing = 50  # 小按钮间距
        
        small_buttons = ["帮助", "关于", "退出登录"] if draw_buttons else ["帮助", "关于", "退出"]
        total_width = (len(small_buttons) * small_btn_width) + ((len(small_buttons) - 1) * small_btn_spacing)
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        for i, text in enumerate(small_buttons):
            btn_rect = pygame.Rect(
                start_x + i * (small_btn_width + small_btn_spacing),
                small_btn_y,
                small_btn_width,
                small_btn_height
            )
            # 只绘制文字,不绘制按钮背景
            text_surface = small_font.render(text, True, COLORS['ACCENT'])
            text_rect = text_surface.get_rect(center=btn_rect.center)
            screen.blit(text_surface, text_rect)
            
            btn_rects.append(btn_rect)
    
    return btn_rects

def draw_leaderboard(screen, font, small_font, db, scroll_y=0, is_scrolling=False):
    """
    绘制排行榜界面
    scroll_y: 当前滚动位置
    is_scrolling: 是否正在滚动
    """
    screen.fill(COLORS['DARK'])
    
    # 绘制标题
    title = font.render("排行榜", True, COLORS['ACCENT'])
    title_rect = title.get_rect(centerx=SCREEN_WIDTH//2, top=120)
    screen.blit(title, title_rect)
    
    # 获取所有用户的最高分
    high_scores = db.get_high_scores()  # 不限制数量
    
    if not high_scores:
        no_scores = small_font.render("暂无记录", True, COLORS['LIGHT'])
        no_scores_rect = no_scores.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(no_scores, no_scores_rect)
        return None, None, None
    
    # 计算可显示的记录数量
    visible_rows = 10  # 一页显示的行数
    row_height = 40   # 每行高度
    total_rows = len(high_scores)
    max_scroll = max(0, total_rows - visible_rows)
    
    # 创建滚动区域
    scroll_area = pygame.Surface((400, row_height * visible_rows))
    scroll_area.fill(COLORS['DARK'])
    
    # 绘制表头
    header_y = title_rect.bottom + 30
    pygame.draw.line(screen, COLORS['LIGHT'],
                    (SCREEN_WIDTH//2 - 200, header_y),
                    (SCREEN_WIDTH//2 + 200, header_y))
    
    username_header = small_font.render("用户名", True, COLORS['ACCENT'])
    score_header = small_font.render("最高分", True, COLORS['ACCENT'])
    screen.blit(username_header, (SCREEN_WIDTH//2 - 150, header_y + 10))
    score_header_rect = score_header.get_rect(right=SCREEN_WIDTH//2 + 150)
    screen.blit(score_header, (score_header_rect.x, header_y + 10))
    
    # 绘制分割线
    pygame.draw.line(screen, COLORS['LIGHT'],
                    (SCREEN_WIDTH//2 - 200, header_y + 40),
                    (SCREEN_WIDTH//2 + 200, header_y + 40))
    
    # 内容区域
    content_start_y = header_y + 50
    content_height = visible_rows * row_height
    
    # 绘制记录时考虑滚动位置
    start_y = content_start_y - scroll_y
    for i, (username, score, _) in enumerate(high_scores):
        y = start_y + i * 40  # 40是每行高度
        
        # 只绘制可见区域内的内容
        if content_start_y <= y <= content_start_y + content_height:
            # 绘制排名
            rank = f"#{i+1}"
            rank_text = small_font.render(rank, True, COLORS['ACCENT'])
            screen.blit(rank_text, (SCREEN_WIDTH//2 - 190, y))
            
            # 绘制用户名
            name_text = small_font.render(username, True, COLORS['LIGHT'])
            screen.blit(name_text, (SCREEN_WIDTH//2 - 150, y))
            
            # 绘制分数
            score_text = small_font.render(str(score), True, COLORS['LIGHT'])
            score_rect = score_text.get_rect(right=SCREEN_WIDTH//2 + 150)
            screen.blit(score_text, (score_rect.x, y))
    
    # 只在滚动时绘制滚动条
    if is_scrolling and len(high_scores) > visible_rows:
        # 计算滚动条高度和位置
        content_height = visible_rows * 40  # 可见区域高度
        total_height = len(high_scores) * 40  # 总内容高度
        scroll_height = content_height * (content_height / total_height)  # 滚动条高度
        scroll_pos = content_start_y + (scroll_y / max_scroll) * (content_height - scroll_height)
        
        # 绘制滚动条背景
        scroll_bar_bg = pygame.Rect(
            SCREEN_WIDTH//2 + 210, 
            content_start_y, 
            6, 
            content_height
        )
        pygame.draw.rect(screen, COLORS['PRIMARY'], scroll_bar_bg, border_radius=3)
        
        # 绘制滚动条
        scroll_bar = pygame.Rect(
            SCREEN_WIDTH//2 + 210,
            scroll_pos,
            6,
            scroll_height
        )
        pygame.draw.rect(screen, COLORS['ACCENT'], scroll_bar, border_radius=3)
    
    # 绘制返回按钮
    btn_width, btn_height = 200, 50
    back_btn = pygame.Rect(
        SCREEN_WIDTH//2 - btn_width//2,
        SCREEN_HEIGHT - 100,
        btn_width,
        btn_height
    )
    pygame.draw.rect(screen, COLORS['PRIMARY'], back_btn, border_radius=8)
    back_text = small_font.render("返回 (B)", True, COLORS['LIGHT'])
    text_rect = back_text.get_rect(center=back_btn.center)
    screen.blit(back_text, text_rect)
    
    return back_btn  # 只返回返回按钮的 Rect 对象

def draw_two_player_game(screen, small_font, game):
    """绘制双人游戏界面"""
    # 计算缩放尺寸和位置
    scale = 0.8  # 将游戏板缩小
    scaled_grid = int(GRID_SIZE * scale)
    scaled_board_width = BOARD_WIDTH * scaled_grid
    scaled_board_height = BOARD_HEIGHT * scaled_grid
    
    # 计算两个游戏板的位置，使其水平居中
    total_width = scaled_board_width * 2 + 100  # 两个游戏板加间距的总宽度
    left_x = (SCREEN_WIDTH - total_width) // 2 + 10  # 右侧游戏板起始x坐标
    right_x = left_x + scaled_board_width + 100 - 20 # 左侧游戏板起始x坐标
    top_y = 100  # 顶部留出空间

    # 在游戏板上方添加标识文字
    if isinstance(game, AIGame):
        # 创建更大字号的字体
        title_font = font_manager.get_font(40)  # 设置字号为30
        
        # AI模式的标识，使用更大的字体
        ai_text = title_font.render("AI", True, COLORS['ACCENT'])
        player_text = title_font.render("玩家", True, COLORS['ACCENT'])
        
        # 计算文字位置并绘制
        ai_rect = ai_text.get_rect(centerx=left_x + scaled_board_width//2, bottom=top_y - 30)
        player_rect = player_text.get_rect(centerx=right_x + scaled_board_width//2, bottom=top_y - 30)
        
        screen.blit(ai_text, ai_rect)
        screen.blit(player_text, player_rect)
    else:
        # 普通双人模式的标识也使用更大字体
        title_font = font_manager.get_font(40)
        p1_text = title_font.render("玩家1", True, COLORS['ACCENT'])
        p2_text = title_font.render("玩家2", True, COLORS['ACCENT'])
        
        # 计算文字位置并绘制
        p1_rect = p1_text.get_rect(centerx=left_x + scaled_board_width//2, bottom=top_y - 30)
        p2_rect = p2_text.get_rect(centerx=right_x + scaled_board_width//2, bottom=top_y - 30)
        
        screen.blit(p1_text, p1_rect)
        screen.blit(p2_text, p2_rect)
    
    # 绘制游戏边框和背景
    for x, board in [(left_x, game.player1['board']), (right_x, game.player2['board'])]:
        
        # 绘制游戏板边框
        border_rect = pygame.Rect(x-2, top_y-2, scaled_board_width+4, scaled_board_height+4)
        pygame.draw.rect(screen, COLORS['LIGHT'], border_rect, 2)
        if settings.SHOW_GRID:
            # 绘制游戏板网格
            for row in range(BOARD_HEIGHT):
                for col in range(BOARD_WIDTH):
                    grid_rect = pygame.Rect(
                        x + col * scaled_grid,
                        top_y + row * scaled_grid,
                        scaled_grid - 1,
                        scaled_grid - 1
                    )
                    pygame.draw.rect(screen, COLORS['PRIMARY'], grid_rect, 1)
    
    # 绘制两个玩家的方块
    for x, board in [(left_x, game.player1['board']), (right_x, game.player2['board'])]:
        # 绘制已固定的方块
        for row in range(BOARD_HEIGHT):
            for col in range(BOARD_WIDTH):
                cell = board.board[row][col]
                if cell:
                    block_rect = pygame.Rect(
                        x + col * scaled_grid,
                        top_y + row * scaled_grid,
                        scaled_grid - 1,
                        scaled_grid - 1
                    )
                    pygame.draw.rect(screen, COLORS[cell], block_rect)
        
        # 绘制当前下落的方块
        if board.current_piece:
            piece = board.current_piece
            for row in range(len(piece.shape)):
                for col in range(len(piece.shape[row])):
                    if piece.shape[row][col]:
                        block_rect = pygame.Rect(
                            x + (piece.x + col) * scaled_grid,
                            top_y + (piece.y + row) * scaled_grid,
                            scaled_grid - 1,
                            scaled_grid - 1
                        )
                        pygame.draw.rect(screen, COLORS[piece.type], block_rect)
    
    # 在游戏板下方绘制信息和按钮
    info_y = top_y + scaled_board_height + 20
    
    # 计算每个玩家的按钮区域宽度
    button_area_width = scaled_board_width  # 按钮区域宽度等于游戏板宽度
    
    for x, player_num, board in [
        (left_x, "1", game.player1['board']),
        (right_x, "2", game.player2['board'])
    ]:
        # 计算得分显示的位置（在按钮上方）
        score_y = info_y + 20  # 得分显示的y坐标
        
        # 绘制得分
        score_text = small_font.render(f"得分: {board.score}", True, COLORS['LIGHT'])
        lines_text = small_font.render(f"消除行数: {board.lines}", True, COLORS['LIGHT'])
        
        # 计算文本的居中位置
        score_x = x + (scaled_board_width - score_text.get_width()) // 2
        lines_x = x + (scaled_board_width - lines_text.get_width()) // 2
        
        # 绘制得分和行数
        screen.blit(score_text, (score_x, score_y))
        screen.blit(lines_text, (lines_x, score_y + 25))
        
        # 计算按钮的水平居中位置（在得分显示下方）
        btn_width = 80
        btn_height = 35
        btn_spacing = 20
        total_btn_width = (btn_width * 2) + btn_spacing
        
        # 计算第一个按钮的起始x坐标，使两个按钮在游戏板下方居中
        start_x = x + (scaled_board_width - total_btn_width) // 2
        
        # 创建和绘制按钮（在得分显示下方）
        pause_btn = pygame.Rect(start_x, info_y + 80, btn_width, btn_height)
        drop_btn = pygame.Rect(start_x + btn_width + btn_spacing, info_y + 80, btn_width, btn_height)
        
        # 绘制按钮背景
        pygame.draw.rect(screen, COLORS['PRIMARY'] if not board.is_paused else COLORS['SECONDARY'], pause_btn)
        pygame.draw.rect(screen, COLORS['PRIMARY'], drop_btn)
        
        # 绘制按钮文本
        pause_text = small_font.render("继续" if board.is_paused else "暂停", True, COLORS['LIGHT'])
        drop_text = small_font.render("下落", True, COLORS['LIGHT'])
        
        screen.blit(pause_text, (pause_btn.centerx - pause_text.get_width()//2, pause_btn.y + 8))
        screen.blit(drop_text, (drop_btn.centerx - drop_text.get_width()//2, drop_btn.y + 8))
        
        # 存储按钮引用
        if player_num == "1":
            p1_pause_btn = pause_btn
            p1_drop_btn = drop_btn
        else:
            p2_pause_btn = pause_btn
            p2_drop_btn = drop_btn
    
    return ((p1_pause_btn, p1_drop_btn), (p2_pause_btn, p2_drop_btn))

def draw_pause_menu(screen, small_font):
    """绘制暂停菜单"""
    # 创建半透明背景
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(180)
    screen.blit(overlay, (0, 0))
    
    # 设置按钮尺寸和位置
    btn_width = 200
    btn_height = 50
    btn_spacing = 20
    
    # 计算按钮位置使其居中
    resume_btn = pygame.Rect(
        SCREEN_WIDTH//2 - btn_width//2,
        SCREEN_HEIGHT//2 - btn_height - btn_spacing//2,
        btn_width,
        btn_height
    )
    menu_btn = pygame.Rect(
        SCREEN_WIDTH//2 - btn_width//2,
        SCREEN_HEIGHT//2 + btn_spacing//2,
        btn_width,
        btn_height
    )
    
    # 绘制按钮
    for btn in [resume_btn, menu_btn]:
        pygame.draw.rect(screen, COLORS['PRIMARY'], btn, border_radius=8)
    
    # 绘制按钮文本
    resume_text = small_font.render("继续游戏 (P)", True, COLORS['LIGHT'])
    menu_text = small_font.render("返回主菜单 (M)", True, COLORS['LIGHT'])
    
    # 居中显示文本
    resume_text_rect = resume_text.get_rect(center=resume_btn.center)
    menu_text_rect = menu_text.get_rect(center=menu_btn.center)
    
    screen.blit(resume_text, resume_text_rect)
    screen.blit(menu_text, menu_text_rect)
    
    return resume_btn, menu_btn

def draw_settings_button(screen):
    """在右上角绘制设置图标"""
    # 计算图标位置（右上角，留出边距）
    icon_x = SCREEN_WIDTH - SETTINGS_ICON.get_width() - 20
    icon_y = 20
    
    # 绬制图标
    screen.blit(SETTINGS_ICON, (icon_x, icon_y))
    
    # 返回图标的矩形区域用于检测点击
    return pygame.Rect(icon_x, icon_y, SETTINGS_ICON.get_width(), SETTINGS_ICON.get_height())

def draw_settings_menu(screen, small_font):
    """绘制设置菜单"""
    # 设置菜单背景
    menu_width = 300
    menu_height = 200
    menu_x = (SCREEN_WIDTH - menu_width) // 2
    menu_y = (SCREEN_HEIGHT - menu_height) // 2
    menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
    
    # 绘制半透明背景
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(180)
    screen.blit(overlay, (0, 0))
    
    # 绘制菜单背景
    pygame.draw.rect(screen, COLORS['DARK'], menu_rect)
    pygame.draw.rect(screen, COLORS['PRIMARY'], menu_rect, 2)
    
    # 绘制标题
    title = small_font.render("设置", True, COLORS['LIGHT'])
    title_rect = title.get_rect(midtop=(menu_rect.centerx, menu_rect.top + 20))
    screen.blit(title, title_rect)
    
    # 网格显示设置
    grid_text = small_font.render("网格", True, COLORS['LIGHT'])
    grid_text_rect = grid_text.get_rect(x=menu_x + 30, centery=menu_y + 80)
    screen.blit(grid_text, grid_text_rect)
    
    # 音效设置
    sound_text = small_font.render("音效", True, COLORS['LIGHT'])
    sound_text_rect = sound_text.get_rect(x=menu_x + 30, centery=menu_y + 120)
    screen.blit(sound_text, sound_text_rect)
    
    # 绘制开关按钮
    toggle_width = 50
    toggle_height = 24
    toggle_x = menu_x + menu_width - 80
    toggle_y = grid_text_rect.centery - toggle_height//2
    toggle_rect = pygame.Rect(toggle_x, toggle_y, toggle_width, toggle_height)
    
    sound_toggle_x = toggle_x
    sound_toggle_y = sound_text_rect.centery - toggle_height//2
    sound_toggle_rect = pygame.Rect(sound_toggle_x, sound_toggle_y, toggle_width, toggle_height)
    
    pygame.draw.rect(screen, 
                    COLORS['ACCENT'] if settings.SHOW_GRID else COLORS['PRIMARY'], 
                    toggle_rect, 
                    border_radius=12)
    pygame.draw.rect(screen, 
                    COLORS['ACCENT'] if settings.SOUND_ENABLED else COLORS['PRIMARY'], 
                    sound_toggle_rect, 
                    border_radius=12)
    
    # 绘制滑块
    circle_radius = toggle_height//2 - 2
    for rect, enabled in [(toggle_rect, settings.SHOW_GRID), 
                         (sound_toggle_rect, settings.SOUND_ENABLED)]:
        circle_x = rect.right - circle_radius if enabled else rect.left + circle_radius
        pygame.draw.circle(screen, COLORS['LIGHT'],
                         (circle_x, rect.centery),
                         circle_radius)
    
    # 关闭按钮
    close_btn = pygame.Rect(menu_rect.right - 30, menu_rect.top + 10, 20, 20)
    pygame.draw.line(screen, COLORS['LIGHT'], 
                    (close_btn.left + 5, close_btn.top + 5),
                    (close_btn.right - 5, close_btn.bottom - 5), 2)
    pygame.draw.line(screen, COLORS['LIGHT'],
                    (close_btn.left + 5, close_btn.bottom - 5),
                    (close_btn.right - 5, close_btn.top + 5), 2)
    
    # 确保返回三个值
    return toggle_rect, sound_toggle_rect, close_btn

def draw_powerup_buttons(screen, small_font):
    """绘制道具按钮"""
    # 按钮尺寸和位置
    btn_size = 50
    btn_spacing = 100
    bottom_margin = 60
    
    # 计算总宽度和起始位置
    total_width = btn_size * 3 + btn_spacing * 2
    start_x = (SCREEN_WIDTH - total_width) // 2
    y = SCREEN_HEIGHT - bottom_margin - btn_size

    button_rects = {}
    
    # 绘制三个道具按钮
    for i, (powerup_type, info) in enumerate(POWERUPS.items()):
        # 计算按钮位置
        x = start_x + (btn_size + btn_spacing) * i
        btn_rect = pygame.Rect(x, y, btn_size, btn_size)
        
        # 绘制按钮背景
        pygame.draw.rect(screen, COLORS['PRIMARY'], btn_rect, border_radius=5)
        
            # 加载并绘制图标
        icon = pygame.image.load(info['icon_path'])
        icon = pygame.transform.scale(icon, (btn_size - 10, btn_size - 10))
        icon_rect = icon.get_rect(center=btn_rect.center)
        screen.blit(icon, icon_rect)

        
        
        # 显示价格
        cost_text = small_font.render(f"{info['cost']}分", True, COLORS['LIGHT'])
        cost_rect = cost_text.get_rect(centerx=btn_rect.centerx, top=btn_rect.bottom + 5)
        screen.blit(cost_text, cost_rect)
        
        button_rects[powerup_type] = btn_rect
    
    return button_rects

def draw_help_screen(screen, font, small_font):
    """绘制帮助界面"""
    screen.fill(COLORS['DARK'])
    
    # 绘制标题
    title = font.render("游戏帮助", True, COLORS['ACCENT'])
    title_rect = title.get_rect(centerx=SCREEN_WIDTH//2, top=50)
    screen.blit(title, title_rect)
    
    # 定义帮助文本内容
    help_texts = [
        ("游戏模式:", ""),
        ("无尽模式", "- 无时间限制,持续游戏直到失败"),
        ("限时模式", "- 在180秒内获得尽可能高的分数"),
        ("双人模式", "- 与另一位玩家一起游戏,相互竞争"),
        ("人机模式", "- 与AI对战,体现人类智慧,战胜AI"),
        "",
        ("操作方式:", ""),
        ("方向键", "- 移动和旋转方块"),
        ("空格键", "- 快速下落"),
        ("P键", "- 暂停游戏"),
        "",
        ("道具系统(使用已获得的分数来换取):", ""),
        ("炸弹", "- 消除最下面一行(200分)"),
        ("闪电", "- 清除所有方块(1000分)"),
        ("垃圾桶", "- 跳过当前方块(100分)"),
        "",
        ("双人模式特殊规则:", ""),
        ("消除2行", "- 向对手发送1行垃圾行"),
        ("消除3行", "- 向对手发送2行垃圾行"),
        ("消除4行以上", "- 向对手发送4行垃圾行")
    ]
    
    # 绘制帮助文本
    y_offset = 120
    line_height = 25
    left_margin = SCREEN_WIDTH//4 - 50
    
    for text_line in help_texts:
        if isinstance(text_line, tuple):
            title, content = text_line
            if title:
                title_surface = small_font.render(title, True, COLORS['ACCENT'])
                screen.blit(title_surface, (left_margin, y_offset))
            if content:
                content_surface = small_font.render(content, True, COLORS['LIGHT'])
                screen.blit(content_surface, (left_margin + 150, y_offset))
        elif isinstance(text_line, str) and text_line == "":
            # 空行处理
            pass
        y_offset += line_height
    
    # 绘制返回按钮
    btn_width = 200
    btn_height = 50
    back_btn = pygame.Rect(
        SCREEN_WIDTH//2 - btn_width//2,
        SCREEN_HEIGHT - 100,
        btn_width,
        btn_height
    )
    
    pygame.draw.rect(screen, COLORS['PRIMARY'], back_btn, border_radius=8)
    back_text = small_font.render("返回 (B)", True, COLORS['LIGHT'])
    text_rect = back_text.get_rect(center=back_btn.center)
    screen.blit(back_text, text_rect)
    
    return back_btn

def draw_about_screen(screen, font, small_font):
    """绘制关于界面"""
    screen.fill(COLORS['DARK'])
    
    # 创建更大的字体用于主标题
    title_font = font_manager.get_font(40)  # 设置更大的字号
    
    # 绘制主标题
    title = title_font.render("关于TetraNova：重构方块世界", True, COLORS['ACCENT'])
    title_rect = title.get_rect(centerx=SCREEN_WIDTH//2, top=80)
    screen.blit(title, title_rect)
    
    
        # 加载并显示游戏图标
    icon = pygame.image.load('assets/images/game_icon.png')  # 确保图标文件存在
    icon = pygame.transform.scale(icon, (200, 200))
    icon_rect = icon.get_rect(centerx=SCREEN_WIDTH//2, top=title_rect.bottom + 40)
    screen.blit(icon, icon_rect)
    last_bottom = icon_rect.bottom
    
    
    # 定义关于信息
    about_texts = [
        ("版本", "2.0"),
        ("开发者", "肘子 Copilot"),
        ("联系方式", "lxz8763@icloud.com"),
        ("", ""),  # 空行
        ("", "有什么建议欢迎联系我们哦~"),
    ]
    
    # 绘制关于信息
    y_offset = last_bottom + 60
    line_height = 40
    left_margin = SCREEN_WIDTH//2 - 200
    
    for label, content in about_texts:
        if label:
            # 绘制标签
            label_surface = small_font.render(label + ":", True, COLORS['ACCENT'])
            screen.blit(label_surface, (left_margin, y_offset))
            
            # 绘制内容
            content_surface = small_font.render(content, True, COLORS['LIGHT'])
            screen.blit(content_surface, (left_margin + 150, y_offset))
        elif content:  # 只有内容没有标签的行（用于显示提示信息）
            content_surface = small_font.render(content, True, COLORS['LIGHT'])
            content_rect = content_surface.get_rect(centerx=SCREEN_WIDTH//2, top=y_offset)
            screen.blit(content_surface, content_rect)
        
        y_offset += line_height
    
    # 绘制返回按钮
    btn_width = 200
    btn_height = 50
    back_btn = pygame.Rect(
        SCREEN_WIDTH//2 - btn_width//2,
        SCREEN_HEIGHT - 100,
        btn_width,
        btn_height
    )
    
    pygame.draw.rect(screen, COLORS['PRIMARY'], back_btn, border_radius=8)
    back_text = small_font.render("返回 (B)", True, COLORS['LIGHT'])
    text_rect = back_text.get_rect(center=back_btn.center)
    screen.blit(back_text, text_rect)
    
    return back_btn
