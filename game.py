import pygame
import sys
from config import (
    COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, 
    MENU, RUNNING, ENDLESS_MODE, TIMED_MODE, LOGIN, LEADERBOARD, AI_MODE,
    settings,
    BOARD_WIDTH, BOARD_HEIGHT, HELP, ABOUT  # 添加这一行
)
from board import GameBoard
from ui import draw_board, draw_side_panel, draw_game_over, draw_start_menu, update_menu_decor_blocks
import ui
from player import HumanPlayer
from login import LoginScreen
from database import GameDatabase
from two_player import TwoPlayerGame
from ai_game import AIGame
from sound_manager import SoundManager 
from font_manager import FontManager

font_manager = FontManager()

def main():
    
    # 初始化pygame和字体
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("俄罗斯方块")
    font = font_manager.get_font(50)
    small_font = font_manager.get_font(20)
    
    # 初始化数据库
    db = GameDatabase()
    
    # 游戏状态与对象初始化
    game_state = LOGIN
    game = GameBoard()
    player = HumanPlayer(game)
    menu_btn_rects = []
    last_decor_update = pygame.time.get_ticks()
    decor_update_interval = 1000  # 每秒更新一次装饰方块

    # 初始化排行榜滚动相关变量
    scroll_y = 0
    max_scroll = 0
    is_scrolling = False
    scroll_timer = 0
    SCROLL_DISPLAY_TIME = 1000  # 滚动条显示时间（毫秒）
    
    # 添加登录状态和对象
    login_screen = LoginScreen(screen, font, small_font, db)
    current_user = None
    
    # 双人游戏对象
    two_player_game = None
    
    # 添加面板变量初始化
    left_panel = None
    right_panel = None
    
    # 在主循环外初始化 button_data
    button_data = None
    
    # 添加设置菜单显示状态
    show_settings = False
    
    # 用于存储HELP和ABOUT状态的back_btn
    help_back_btn = None
    about_back_btn = None
    close_btn = None
    toggle_rect = None
    sound_toggle_rect = None  # 添加这行
    powerup_rects = {}
    settings_btn = None
    
    # 初始化音效管理器
    sound_manager = SoundManager()
    sound_manager.play_bgm()
    
    # 在main函数开始处添加变量
    previous_state = None  # 用于记录前一个状态
    
    while True:
        screen.fill(COLORS['DARK'])
        now = pygame.time.get_ticks()
        

        # 事件处理
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # 如果设置菜单打开，只处理设置菜单的事件
            if show_settings:
                # 保存当前屏幕状态
                background = screen.copy()
                
                # 绘制半透明背景
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.fill((0, 0, 0))
                overlay.set_alpha(180)
                screen.blit(overlay, (0, 0))
                
                # 绘制设置菜单
                grid_toggle_rect, sound_toggle_rect, close_btn = ui.draw_settings_menu(screen, small_font)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    if sound_toggle_rect.collidepoint(x, y):
                        settings.SOUND_ENABLED = not settings.SOUND_ENABLED
                        sound_manager.toggle_sound()
                        sound_manager.play_sound('click')
                    elif close_btn and close_btn.collidepoint(x, y):
                        show_settings = False
                    elif toggle_rect and toggle_rect.collidepoint(x, y):
                        settings.SHOW_GRID = not settings.SHOW_GRID  # 使用settings实例
                        if settings.SOUND_ENABLED:
                            sound_manager.play_sound('click')
                    elif sound_toggle_rect and sound_toggle_rect.collidepoint(x, y):
                        settings.SOUND_ENABLED = not settings.SOUND_ENABLED
                        sound_manager.enabled = settings.SOUND_ENABLED  # 同步状态
                        sound_manager.toggle_sound()
                        if settings.SOUND_ENABLED:
                            sound_manager.play_sound('click')
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # 添加ESC键关闭设置菜单
                        show_settings = False
                # 设置菜单打开时，不处理其他事件
                continue
            
            # 设置菜单关闭时，正常处理其他事件（只在非游戏运行时处理设置按钮）
            if event.type == pygame.MOUSEBUTTONDOWN and game_state != RUNNING:
                x, y = pygame.mouse.get_pos()
                if settings_btn and settings_btn.collidepoint(x, y):
                    show_settings = True
   

            # 登录界面事件处理
            if game_state == LOGIN:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    menu_btn_rects = ui.draw_start_menu(screen, font, small_font, draw_buttons=False)
                    
                    # 检查底部按钮点击
                    if len(menu_btn_rects) >= 3:  # 确保有足够的按钮
                        help_btn = menu_btn_rects[-3]  # 倒数第三个是帮助按钮
                        about_btn = menu_btn_rects[-2]  # 倒数第二个是关于按钮
                        exit_btn = menu_btn_rects[-1]   # 最后一个是退出按钮
                        
                        if help_btn.collidepoint(x, y):
                            if settings.SOUND_ENABLED:
                                sound_manager.play_sound('click')
                            previous_state = LOGIN  # 记录当前状态
                            game_state = HELP
                            continue
                        elif about_btn.collidepoint(x, y):
                            if settings.SOUND_ENABLED:
                                sound_manager.play_sound('click')
                            previous_state = LOGIN  # 记录当前状态
                            game_state = ABOUT
                            continue
                        elif exit_btn.collidepoint(x, y):
                            if settings.SOUND_ENABLED:
                                sound_manager.play_sound('click')
                            pygame.quit()
                            sys.exit()
                    
                    username_rect, password_rect, login_btn_rect, switch_rect = login_screen.draw()
                    
                    if settings.SOUND_ENABLED:
                        sound_manager.play_sound('click')  # 添加按钮点击音效
                    
                    if username_rect.collidepoint(x, y):
                        login_screen.active_field = username_rect
                    elif password_rect.collidepoint(x, y):
                        login_screen.active_field = password_rect
                    elif login_btn_rect.collidepoint(x, y):
                        if login_screen.is_registering:
                            # 注册逻辑
                            if len(login_screen.username) < 3:
                                login_screen.error_message = "用户名至少需要3个字符"
                            elif len(login_screen.password) < 6:
                                login_screen.error_message = "密码至少需要6个字符"
                            else:
                                user_id = db.register_user(login_screen.username, login_screen.password)
                                if user_id:
                                    current_user = user_id
                                    game_state = MENU
                                else:
                                    login_screen.error_message = "用户名已存在"
                        else:
                            # 登录逻辑
                            user_id = db.verify_login(login_screen.username, login_screen.password)
                            if user_id:
                                current_user = user_id
                                game_state = MENU
                            else:
                                login_screen.error_message = "用户名或密码错误"
                    elif switch_rect.collidepoint(x, y):  # 添加切换注册/登录的处理
                        login_screen.is_registering = not login_screen.is_registering
                        login_screen.error_message = ""  # 清除错误信息
                elif event.type == pygame.KEYDOWN:
                    if login_screen.handle_input(event):
                        user_id = login_screen.try_login()
                        if user_id:
                            current_user = user_id
                            game_state = MENU

            # 菜单界面事件处理
            elif game_state == MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    if settings.SOUND_ENABLED:
                        sound_manager.play_sound('click')  # 添加按钮点击音效

                    # 在菜单按钮点击处理部分
                    for idx, rect in enumerate(menu_btn_rects):
                        if rect.collidepoint(x, y):
                            if idx == 4:  # 排行榜按钮
                                game_state = LEADERBOARD
                            elif idx == 5:  # 帮助按钮
                                previous_state = MENU  # 记录当前状态
                                game_state = HELP
                            elif idx == 6:  # 关于按钮
                                previous_state = MENU  # 记录当前状态
                                game_state = ABOUT
                            elif idx == 7:  # 退出登录按钮
                                # 重置当前用户
                                current_user = None
                                # 切换到登录界面
                                game_state = LOGIN
                                # 播放按钮音效
                                if settings.SOUND_ENABLED:
                                    sound_manager.play_sound('click')
                            else:  # 游戏模式按钮
                                game_state = RUNNING
                                if idx == 0:  # 无尽模式
                                    game = GameBoard(ENDLESS_MODE)
                                    player = HumanPlayer(game)
                                elif idx == 1:  # 限时模式
                                    game = GameBoard(TIMED_MODE)
                                    player = HumanPlayer(game)
                                elif idx == 2:  # 双人模式
                                    two_player_game = TwoPlayerGame()
                                    game = two_player_game
                                elif idx == 3:  # 人机模式
                                    game = AIGame()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # 按Esc键退出游戏
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_s:  # 按S键切换设置菜单
                        show_settings = not show_settings

            # 排行榜界面事件处理
            elif game_state == LEADERBOARD:
                now = pygame.time.get_ticks()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    if settings.SOUND_ENABLED:
                        sound_manager.play_sound('click')  # 添加按钮点击音效

                    if back_btn and back_btn.collidepoint(x, y):
                        game_state = MENU
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_b:  # 按B返回
                        game_state = MENU
                elif event.type == pygame.MOUSEWHEEL:  # 添加鼠标滚轮事件处理
                    old_scroll_y = scroll_y
                    scroll_y = max(0, min(max_scroll, scroll_y - event.y * 20))
                    if old_scroll_y != scroll_y:  # 如果滚动位置改变
                        is_scrolling = True
                        scroll_timer = now  # 重置计时器
            
            # 检查是否需要隐藏滚动条
            if is_scrolling and now - scroll_timer > SCROLL_DISPLAY_TIME:
                is_scrolling = False
            
            # HELP界面事件处理
            elif game_state == HELP:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    if help_back_btn and help_back_btn.collidepoint(x, y):
                        if settings.SOUND_ENABLED:
                            sound_manager.play_sound('click')
                        game_state = previous_state  # 返回到前一个状态
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_b or event.key == pygame.K_ESCAPE:  # 按B或ESC返回
                        if settings.SOUND_ENABLED:
                            sound_manager.play_sound('click')
                        game_state = previous_state  # 返回到前一个状态
            
            # ABOUT界面事件处理
            elif game_state == ABOUT:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    if about_back_btn and about_back_btn.collidepoint(x, y):
                        if settings.SOUND_ENABLED:
                            sound_manager.play_sound('click')
                        game_state = previous_state  # 返回到前一个状态
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_b or event.key == pygame.K_ESCAPE:  # 按B或ESC返回
                        if settings.SOUND_ENABLED:
                            sound_manager.play_sound('click')
                        game_state = previous_state  # 返回到前一个状态
            
            # 游戏主界面事件处理
            elif game_state == RUNNING:
                # 键盘事件处理
                if event.type == pygame.KEYDOWN:
                    if game.is_game_over:  # 游戏结束时的按键处理
                        if event.key == pygame.K_r:  # 按R重新开始
                            if isinstance(game, AIGame):
                                game = AIGame()  # 重新开始人机游戏
                            elif isinstance(game, TwoPlayerGame):
                                game = TwoPlayerGame()  # 重新开始双人游戏
                            else:
                                game = GameBoard(game.mode)
                                player = HumanPlayer(game)
                        elif event.key == pygame.K_m:  # 按M返回菜单
                            game_state = MENU
                    else:  # 游戏进行中的按键处理
                        if isinstance(game, AIGame):
                            # 人机模式：AI控制玩家1，玩家控制玩家2（方向键）
                            if game.player2['board'].is_paused:
                                if event.key == pygame.K_m:  # M键返回主菜单
                                    game_state = MENU
                                    continue
                            
                            if not game.is_game_over and not game.player2['board'].is_paused:
                                # 玩家控制 (方向键 + 回车)
                                if event.key == pygame.K_LEFT:
                                    game.player2['board'].move('left')
                                elif event.key == pygame.K_RIGHT:
                                    game.player2['board'].move('right')
                                elif event.key == pygame.K_DOWN:
                                    game.player2['board'].move('down')
                                elif event.key == pygame.K_UP:
                                    game.player2['board'].rotate()
                                    if settings.SOUND_ENABLED:
                                        sound_manager.play_sound('rotate')
                                elif event.key == pygame.K_RETURN:
                                    game.player2['board'].hard_drop()
                                    if settings.SOUND_ENABLED:
                                        sound_manager.play_sound('drop')
                                elif event.key == pygame.K_o:
                                    game.player2['board'].is_paused = not game.player2['board'].is_paused
                        elif isinstance(game, TwoPlayerGame):
                            # 双人模式的按键处理
                            if game.player1['board'].is_paused or game.player2['board'].is_paused:
                                if event.key == pygame.K_m:  # M键返回主菜单
                                    game_state = MENU
                                    continue

                            if not game.is_game_over:
                                # 玩家1控制 (WASD + 空格)
                                if event.key == pygame.K_a:
                                    game.player1['board'].move('left')
                                elif event.key == pygame.K_d:
                                    game.player1['board'].move('right')
                                elif event.key == pygame.K_s:
                                    game.player1['board'].move('down')
                                elif event.key == pygame.K_w:
                                    game.player1['board'].rotate()
                                    if settings.SOUND_ENABLED:
                                        sound_manager.play_sound('rotate')
                                elif event.key == pygame.K_SPACE:
                                    game.player1['board'].hard_drop()
                                    if settings.SOUND_ENABLED:
                                        sound_manager.play_sound('drop')
                                elif event.key == pygame.K_p:
                                    game.player1['board'].is_paused = not game.player1['board'].is_paused
                                
                                # 玩家2控制 (方向键 + 回车)
                                if event.key == pygame.K_LEFT:
                                    game.player2['board'].move('left')
                                elif event.key == pygame.K_RIGHT:
                                    game.player2['board'].move('right')
                                elif event.key == pygame.K_DOWN:
                                    game.player2['board'].move('down')
                                elif event.key == pygame.K_UP:
                                    game.player2['board'].rotate()
                                    if settings.SOUND_ENABLED:
                                        sound_manager.play_sound('rotate')
                                elif event.key == pygame.K_RETURN:
                                    game.player2['board'].hard_drop()
                                    if settings.SOUND_ENABLED:
                                        sound_manager.play_sound('drop')
                                elif event.key == pygame.K_o:
                                    game.player2['board'].is_paused = not game.player2['board'].is_paused
                        else:
                            # 单人模式
                            if event.key == pygame.K_m and game.is_paused:  # 添加暂停时M键返回主菜单
                                game_state = MENU
                                continue  # 跳过其他按键处理
                            elif game.is_game_over and event.key == pygame.K_r:
                                # 游戏结束后按R重开
                                game = GameBoard(game.mode)  # 保持相同的游戏模式
                                player = HumanPlayer(game)
                            elif not game.is_game_over and not game.is_paused:
                                # 正常游戏操作
                                # 支持方向键
                                if event.key == pygame.K_LEFT:
                                    player.handle_key('left')
                                elif event.key == pygame.K_RIGHT:
                                    player.handle_key('right')
                                elif event.key == pygame.K_DOWN:
                                    player.handle_key('down')
                                elif event.key == pygame.K_UP:
                                    player.handle_key('rotate')
                                    if settings.SOUND_ENABLED:
                                        sound_manager.play_sound('rotate')
                                elif event.key == pygame.K_SPACE:
                                    player.handle_key('hard_drop')
                                    if settings.SOUND_ENABLED:
                                        sound_manager.play_sound('drop')
                                # 支持WASD键
                                elif event.key == pygame.K_a:
                                    player.handle_key('left')
                                elif event.key == pygame.K_d:
                                    player.handle_key('right')
                                elif event.key == pygame.K_s:
                                    player.handle_key('down')
                                elif event.key == pygame.K_w:
                                    player.handle_key('rotate')
                                    if settings.SOUND_ENABLED:
                                        sound_manager.play_sound('rotate')
                                elif event.key == pygame.K_p:
                                    player.handle_key('pause')
                
                # 鼠标按钮点击处理
                elif event.type == pygame.MOUSEBUTTONDOWN and button_data is not None:
                    x, y = pygame.mouse.get_pos()

                    if settings.SOUND_ENABLED:
                        sound_manager.play_sound('click')  # 添加按钮点击音效
                    if isinstance(game, TwoPlayerGame):
                        # 处理双人模式的按钮点击
                        if not game.is_game_over:
                            try:
                                p1_buttons, p2_buttons = button_data
                                if p1_buttons and all(p1_buttons):  # 确保玩家1的按钮都存在
                                    if p1_buttons[0].collidepoint(x, y):  # pause_btn
                                        game.toggle_pause()

                                    elif p1_buttons[1].collidepoint(x, y):  # drop_btn
                                        space_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE})
                                        pygame.event.post(space_event)
                                
                                if p2_buttons and all(p2_buttons):  # 确保玩家2的按钮都存在
                                    if p2_buttons[0].collidepoint(x, y):  # pause_btn
                                        game.toggle_pause()
                                    elif p2_buttons[1].collidepoint(x, y):  # drop_btn
                                        return_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN})
                                        pygame.event.post(return_event)
                            except (TypeError, ValueError, AttributeError) as e:
                                print(f"按钮区域未正确初始化: {e}")
                    else:
                        if not game.is_paused and not game.is_game_over and powerup_rects:
                            if powerup_rects.get('bomb') and powerup_rects['bomb'].collidepoint(x, y):
                                if game.score >= 200:
                                    success = game.use_bomb()
                                    if success:
                                        tool_used = True
                                        if settings.SOUND_ENABLED:
                                            sound_manager.play_sound('tool_1')
                                else:
                                    # 显示分数不足提示
                                    confirm_text = small_font.render("分数不足!", True, COLORS['ACCENT'])
                                    text_rect = confirm_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                                    
                                    # 创建半透明背景
                                    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                                    overlay.fill((0, 0, 0))
                                    overlay.set_alpha(180)
                                    screen.blit(overlay, (0, 0))
                                    
                                    # 显示提示文字
                                    screen.blit(confirm_text, text_rect)
                                    pygame.display.flip()
                                    pygame.time.wait(1000)

                            elif powerup_rects.get('lightning') and powerup_rects['lightning'].collidepoint(x, y):
                                if game.score >= 1000:
                                    success = game.use_lightning()
                                    if success:
                                        tool_used = True
                                        if settings.SOUND_ENABLED:
                                            sound_manager.play_sound('tool_3')
                                else:
                                    # 显示分数不足提示
                                    confirm_text = small_font.render("分数不足!", True, COLORS['ACCENT'])
                                    text_rect = confirm_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                                    
                                    # 创建半透明背景
                                    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                                    overlay.fill((0, 0, 0))
                                    overlay.set_alpha(180)
                                    screen.blit(overlay, (0, 0))
                                    
                                    # 显示提示文字
                                    screen.blit(confirm_text, text_rect)
                                    pygame.display.flip()
                                    pygame.time.wait(1000)

                            elif powerup_rects.get('trash') and powerup_rects['trash'].collidepoint(x, y):
                                if game.score >= 100:
                                    success = game.use_trash()
                                    if success:
                                        tool_used = True
                                        if settings.SOUND_ENABLED:
                                            sound_manager.play_sound('tool_2')
                                else:
                                    # 显示分数不足提示
                                    confirm_text = small_font.render("分数不足!", True, COLORS['ACCENT'])
                                    text_rect = confirm_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                                    
                                    # 创建半透明背景
                                    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                                    overlay.fill((0, 0, 0))
                                    overlay.set_alpha(180)
                                    screen.blit(overlay, (0, 0))
                                    
                                    # 显示提示文字
                                    screen.blit(confirm_text, text_rect)
                                    pygame.display.flip()
                                    pygame.time.wait(1000)
                        # 单人模式的按钮点击处理
                        if not game.is_game_over:
                            try:
                                buttons, _ = button_data  # 解包时忽略第二个值
                                if buttons and all(buttons):  # 确保按钮都存在
                                    if buttons[0].collidepoint(x, y):
                                        player.handle_key('pause')
                                    elif buttons[1].collidepoint(x, y):
                                        player.handle_key('hard_drop')
                            except (TypeError, ValueError) as e:
                                print(f"按钮区域未正确初始化: {e}")
            

        # 界面绘制
        if game_state == LOGIN:
            # 更新装饰方块
            if now - last_decor_update > decor_update_interval:
                ui.update_menu_decor_blocks()
                last_decor_update = now
            
            # 绘制登录界面的背景和标题
            menu_btn_rects = ui.draw_start_menu(screen, font, small_font, draw_buttons=False)
            
            # 绘制登录界面组件
            settings_btn = ui.draw_settings_button(screen)
            username_rect, password_rect, login_btn_rect, switch_rect = login_screen.draw()
            
            # 如果显示设置菜单则绘制
            if show_settings:
                toggle_rect, sound_toggle_rect, close_btn = ui.draw_settings_menu(screen, small_font)
                
            # # 处理设置按钮点击
            # if event.type == pygame.MOUSEBUTTONDOWN:
            #     x, y = pygame.mouse.get_pos()
            #     if settings_btn and settings_btn.collidepoint(x, y):
            #         show_settings = True
            #     elif show_settings:
            #         if close_btn.collidepoint(x, y):
            #             show_settings = False
            #         elif toggle_rect.collidepoint(x, y):
            #             SHOW_GRID = not SHOW_GRID

        elif game_state == MENU:
            # 更新装饰方块
            if now - last_decor_update > decor_update_interval:
                ui.update_menu_decor_blocks()
                last_decor_update = now
            
            # 绘制主菜单和设置按钮
            menu_btn_rects = ui.draw_start_menu(screen, font, small_font)
            settings_btn = ui.draw_settings_button(screen)
            
            # 如果显示设置菜单则绘制
            if show_settings:
                toggle_rect, sound_toggle_rect, close_btn = ui.draw_settings_menu(screen, small_font)  # 修改这行，解包3个返回值
            
            # # 添加事件处理
            # if event.type == pygame.MOUSEBUTTONDOWN:
            #     x, y = pygame.mouse.get_pos()
            #     if settings_btn and settings_btn.collidepoint(x, y):
            #         show_settings = True
            #     elif show_settings:
            #         if close_btn.collidepoint(x, y):
            #             show_settings = False
            #         elif toggle_rect.collidepoint(x, y):
            #             SHOW_GRID = not SHOW_GRID

        elif game_state == LEADERBOARD:
            # 更新装饰方块
            if now - last_decor_update > decor_update_interval:
                ui.update_menu_decor_blocks()
                last_decor_update = now
            
            # 获取所有用户数量来计算最大滚动值
            all_scores = db.get_high_scores()
            visible_rows = 10  # 一页显示的行数
            max_scroll = max(0, len(all_scores) - visible_rows) * 40  # 40是每行高度
            
            # 绘制排行榜界面，传入滚动状态
            back_btn = ui.draw_leaderboard(
                screen, 
                font, 
                small_font, 
                db, 
                scroll_y, 
                is_scrolling
            )
        elif game_state == HELP:
                # 清空屏幕并填充背景色
                screen.fill(COLORS['DARK'])
                
                # 绘制帮助界面
                help_back_btn = ui.draw_help_screen(screen, font, small_font)
        elif game_state == ABOUT:
            # 清空屏幕并填充背景色
            screen.fill(COLORS['DARK'])
            
            # 绘制关于界面
            about_back_btn = ui.draw_about_screen(screen, font, small_font)
        elif game_state == RUNNING:
            # 修改消除行检查的逻辑
            # 在更新游戏状态之前添加音效检查
            if hasattr(game, 'lines_cleared'):
                cleared = game.lines_cleared
                if settings.SOUND_ENABLED:
                    if cleared >= 3:
                        sound_manager.play_sound('clear_3')
                    elif cleared == 2:
                        sound_manager.play_sound('clear_2')
                    elif cleared == 1:
                        sound_manager.play_sound('clear_1')
                game.lines_cleared = 0  # 重置消行计数

            # 检查双人模式的消除
            if isinstance(game, TwoPlayerGame):
                # 检查玩家1的消除
                if hasattr(game.player1['board'], 'lines_cleared'):
                    cleared = game.player1['board'].lines_cleared
                    if settings.SOUND_ENABLED:
                        if cleared >= 3:
                            sound_manager.play_sound('clear_3')
                        elif cleared == 2:
                            sound_manager.play_sound('clear_2')
                        elif cleared:
                            sound_manager.play_sound('clear_1')
                    game.player1['board'].lines_cleared = 0

                # 检查玩家2的消除
                if hasattr(game.player2['board'], 'lines_cleared'):
                    cleared = game.player2['board'].lines_cleared
                    if settings.SOUND_ENABLED:
                        if cleared >= 3:
                            sound_manager.play_sound('clear_3')
                        elif cleared == 2:
                            sound_manager.play_sound('clear_2')
                        elif cleared:
                            sound_manager.play_sound('clear_1')
                    game.player2['board'].lines_cleared = 0

            # 在检查游戏结束状态时添加游戏结束音效
            if game.is_game_over:
                if settings.SOUND_ENABLED:
                    sound_manager.play_sound('game_over')
                    
            # 更新游戏状态
            game.update()
            
            # 游戏绘制部分
            if isinstance(game, TwoPlayerGame):
                button_data = ui.draw_two_player_game(screen, small_font, game)
                
                # 如果游戏暂停，显示暂停菜单
                if game.is_paused and not game.is_game_over:
                    resume_btn, menu_btn = ui.draw_pause_menu(screen, small_font)
                    
                    # 处理暂停菜单的按钮点击
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = pygame.mouse.get_pos()
                        if settings.SOUND_ENABLED:
                            sound_manager.play_sound('click')
                        
                        if resume_btn.collidepoint(x, y):
                            game.toggle_pause()
                        elif menu_btn.collidepoint(x, y):
                            game_state = MENU
            else:
                # game.update()
                # 单人模式绘制
                draw_board(screen, game.board, game.current_piece)
                button_data = draw_side_panel(screen, small_font, game, game.is_paused, game.is_game_over)
                
                # 只绘制道具按钮，不处理点击
                if not game.is_paused and not game.is_game_over:
                    powerup_rects = ui.draw_powerup_buttons(screen, small_font)
                
                # 如果游戏暂停，显示暂停菜单
                if game.is_paused and not game.is_game_over:
                    resume_btn, menu_btn = ui.draw_pause_menu(screen, small_font)
                    
                    # 处理暂停菜单的按钮点击
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = pygame.mouse.get_pos()
                        # 添加点击音效
                        if settings.SOUND_ENABLED:
                            sound_manager.play_sound('click')
                        
                        if resume_btn.collidepoint(x, y):
                            game.is_paused = False
                        elif menu_btn.collidepoint(x, y):
                            game_state = MENU
            
            # 如果游戏结束且有用户登录，记录分数
            if game.is_game_over and current_user:
                if not isinstance(game, TwoPlayerGame):  # 只记录单人模式的分数
                    mode_str = 'endless' if game.mode == ENDLESS_MODE else 'timed'
                    db.add_game_record(
                        current_user,
                        game.score,
                        game.lines,
                        mode_str
                    )
            
            # 游戏结束界面的按钮事件处理
            if game.is_game_over:
                if isinstance(game, TwoPlayerGame):
                    # 绘制半透明黑色背景
                    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    overlay.fill((0, 0, 0))
                    overlay.set_alpha(180)  # 设置透明度
                    screen.blit(overlay, (0, 0))
                    
                    # 绘制游戏结束标题
                    game_over_text = font.render("游戏结束", True, COLORS['ACCENT'])
                    text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 120))
                    screen.blit(game_over_text, text_rect)
                    
                    # 显示比分
                    score_text = font.render(f"比分: {game.player1['score']} - {game.player2['score']}", True, COLORS['LIGHT'])
                    score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60))
                    screen.blit(score_text, score_rect)
                    
                    # 判断胜负并显示结果
                    if isinstance(game, AIGame):  # 人机模式
                        if game.player1['board'].is_game_over and game.player2['board'].is_game_over:
                            # 两方同时失败，比较分数
                            if game.player1['score'] > game.player2['score']:
                                winner_text = "AI获胜!"
                            else:
                                winner_text = "你赢了AI!"
                        elif game.player1['board'].is_game_over:
                            # AI失败
                            if game.player1['score'] > game.player2['score']:
                                winner_text = "AI获胜!"  # 虽然失败但分数更高
                            else:
                                winner_text = "你赢了AI!"  # AI失败且分数不高
                        elif game.player2['board'].is_game_over:
                            # 玩家失败
                            if game.player2['score'] > game.player1['score']:
                                winner_text = "你赢了AI!"  # 虽然失败但分数更高
                            else:
                                winner_text = "AI获胜!"  # 玩家失败且分数不高
                    else:  # 普通双人模式
                        # 保持原有的双人模式判断逻辑
                        if game.player1['board'].is_game_over and game.player2['board'].is_game_over:
                            if game.player1['score'] > game.player2['score']:
                                winner_text = "玩家1获胜!"
                            elif game.player2['score'] > game.player1['score']:
                                winner_text = "玩家2获胜!"
                            else:
                                winner_text = "平局!"
                        elif game.player1['board'].is_game_over:
                            if game.player1['score'] > game.player2['score']:
                                winner_text = "玩家1获胜!"
                            else:
                                winner_text = "玩家2获胜!"
                        elif game.player2['board'].is_game_over:
                            if game.player2['score'] > game.player1['score']:
                                winner_text = "玩家2获胜!"
                            else:
                                winner_text = "玩家1获胜!"
        
                    winner_color = COLORS['ACCENT']
                    # 绘制结果文本
                    winner_surface = font.render(winner_text, True, winner_color)
                    winner_rect = winner_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                    screen.blit(winner_surface, winner_rect)
                    
                    # 添加重新开始和返回菜单按钮
                    restart_btn = pygame.Rect(SCREEN_WIDTH//2 - 220, SCREEN_HEIGHT//2 + 50, 200, 50)
                    menu_btn = pygame.Rect(SCREEN_WIDTH//2 + 20, SCREEN_HEIGHT//2 + 50, 200, 50)
                    
                    # 绘制按钮背景
                    for btn in [restart_btn, menu_btn]:
                        pygame.draw.rect(screen, COLORS['PRIMARY'], btn, border_radius=8)
                    
                    # 绘制按钮文本
                    restart_text = small_font.render("重新开始 (R)", True, COLORS['LIGHT'])
                    menu_text = small_font.render("返回菜单 (M)", True, COLORS['LIGHT'])
                    
                    restart_text_rect = restart_text.get_rect(center=restart_btn.center)
                    menu_text_rect = menu_text.get_rect(center=menu_btn.center)
                    
                    screen.blit(restart_text, restart_text_rect)
                    screen.blit(menu_text, menu_text_rect)
                else:
                    # 单人模式游戏结束界面
                    restart_btn, menu_btn = draw_game_over(
                        screen, font, small_font, game.is_game_over, game, db, current_user
                    )
                
                # 游戏结束后的按钮事件处理
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    # 添加按钮点击音效
                    if settings.SOUND_ENABLED:
                        sound_manager.play_sound('click')
                        
                    if restart_btn and restart_btn.collidepoint(x, y):
                        if isinstance(game, TwoPlayerGame):
                            if isinstance(game, AIGame):
                                game = AIGame()  # 重新开始人机游戏
                            else:
                                game = TwoPlayerGame()  # 重新开始双人游戏
                        else:
                            game = GameBoard(game.mode)
                            player = HumanPlayer(game)
                    elif menu_btn and menu_btn.collidepoint(x, y):
                        game_state = MENU
                elif event.type == pygame.KEYDOWN:
                    # 添加键盘按键音效
                    if settings.SOUND_ENABLED:
                        sound_manager.play_sound('click')
                        
                    if event.key == pygame.K_r:  # 按R重新开始
                        if isinstance(game, TwoPlayerGame):
                            if isinstance(game, AIGame):
                                game = AIGame()  # 重新开始人机游戏
                            else:
                                game = TwoPlayerGame()  # 重新开始双人游戏
                        else:
                            game = GameBoard(game.mode)
                            player = HumanPlayer(game)
                    elif event.key == pygame.K_m:  # 按M返回菜单
                        game_state = MENU

            
        

        # --- 刷新屏幕 ---
        pygame.display.flip()
        game.clock.tick(60)
        tool_used = False  # 重置道具使用标志

if __name__ == "__main__":
    main()
