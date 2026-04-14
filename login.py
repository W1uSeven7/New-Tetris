import pygame
from config import (
    COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE,
    LOGIN, MENU
)

class LoginScreen:
    def __init__(self, screen, font, small_font, db):
        self.screen = screen
        self.font = font
        self.small_font = small_font
        self.db = db
        self.last_error_time = 0
        self.error_message = ""
        
        # 登录表单状态
        self.username = ""
        self.password = ""
        self.active_field = None  # 当前激活的输入框
        
        # 输入框样式
        input_width = 300
        input_height = 50
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # 创建输入框和按钮的矩形区域
        self.username_rect = pygame.Rect(
            center_x - input_width//2,
            center_y - 60,
            input_width,
            input_height
        )
        
        self.password_rect = pygame.Rect(
            center_x - input_width//2,
            center_y + 20,
            input_width,
            input_height
        )
        
        self.login_btn_rect = pygame.Rect(
            center_x - 100,
            center_y + 100,
            200,
            50
        )

        self.is_registering = False  # 添加注册模式标志

    def draw(self):
        """绘制登录/注册界面"""
        # 绘制标题
        # title_text = "用户注册" if self.is_registering else "用户登录"
        # title = self.font.render(title_text, True, COLORS['ACCENT'])
        # title_rect = title.get_rect(centerx=SCREEN_WIDTH//2, y=120)
        # self.screen.blit(title, title_rect)
        
        # 绘制输入框标签
        username_label = self.small_font.render("用户名", True, COLORS['LIGHT'])
        password_label = self.small_font.render("密码", True, COLORS['LIGHT'])
        self.screen.blit(username_label, (self.username_rect.x, self.username_rect.y - 30))
        self.screen.blit(password_label, (self.password_rect.x, self.password_rect.y - 30))
        
        # 绘制输入框
        for rect, text, is_password in [
            (self.username_rect, self.username, False),
            (self.password_rect, self.password, True)
        ]:
            # 绘制输入框背景
            color = COLORS['PRIMARY'] if self.active_field == rect else COLORS['DARK']
            pygame.draw.rect(self.screen, COLORS['LIGHT'], rect, 2, border_radius=8)
            pygame.draw.rect(self.screen, color, rect.inflate(-4, -4), 0, border_radius=8)
            
            # 绘制输入文本
            display_text = "*" * len(text) if is_password else text
            text_surface = self.small_font.render(display_text, True, COLORS['LIGHT'])
            text_rect = text_surface.get_rect(
                midleft=(rect.left + 10, rect.centery)
            )
            self.screen.blit(text_surface, text_rect)
        
        # 绘制登录/注册按钮
        btn_text = "注册" if self.is_registering else "登录"
        btn_surface = self.small_font.render(btn_text, True, COLORS['LIGHT'])
        btn_rect = btn_surface.get_rect(center=self.login_btn_rect.center)
        pygame.draw.rect(self.screen, COLORS['PRIMARY'], self.login_btn_rect, 0, border_radius=8)
        self.screen.blit(btn_surface, btn_rect)
        
        # 添加切换按钮
        switch_text = "已有账号？去登录" if self.is_registering else "没有账号？去注册"
        switch_surface = self.small_font.render(switch_text, True, COLORS['LIGHT'])
        switch_rect = switch_surface.get_rect(centerx=SCREEN_WIDTH//2, y=self.login_btn_rect.bottom + 20)
        self.screen.blit(switch_surface, switch_rect)
        
        # 显示错误信息
        if self.error_message:
            error_text = self.small_font.render(self.error_message, True, COLORS['Z'])
            error_rect = error_text.get_rect(
                centerx=SCREEN_WIDTH//2,
                top=switch_rect.bottom + 20
            )
            self.screen.blit(error_text, error_rect)
        
        return self.username_rect, self.password_rect, self.login_btn_rect, switch_rect

    def handle_input(self, event):
        """处理输入事件"""
        if event.key == pygame.K_TAB:
            # 在用户名和密码框之间切换
            if self.active_field == self.username_rect:
                self.active_field = self.password_rect
            else:
                self.active_field = self.username_rect
            return False
            
        if event.key == pygame.K_RETURN:
            return True  # 触发登录
            
        if event.key == pygame.K_BACKSPACE:
            # 如果还没有激活任何输入框，默认激活用户名输入框
            if self.active_field is None:
                self.active_field = self.username_rect
            # 删除字符
            if self.active_field == self.username_rect:
                self.username = self.username[:-1]
            elif self.active_field == self.password_rect:
                self.password = self.password[:-1]
        else:
            # 如果用户开始输入但还没有激活任何输入框，默认激活用户名输入框
            if self.active_field is None and event.unicode and event.unicode.isprintable():
                self.active_field = self.username_rect
            # 添加字符（限制长度为20）
            if event.unicode and len(event.unicode) > 0 and event.unicode.isprintable():
                if self.active_field == self.username_rect and len(self.username) < 20:
                    self.username += event.unicode
                elif self.active_field == self.password_rect and len(self.password) < 20:
                    self.password += event.unicode
        return False

    def try_login(self):
        """登录或注册尝试"""
        if not self.username or not self.password:
            self.error_message = "用户名和密码不能为空"
            return None
            
        if self.is_registering:
            # 注册逻辑
            if len(self.username) < 3:
                self.error_message = "用户名至少需要3个字符"
                return None
            if len(self.password) < 6:
                self.error_message = "密码至少需要6个字符"
                return None
            
            # 尝试注册新用户
            user_id = self.db.add_user(self.username, self.password)
            if user_id:
                self.error_message = "注册成功！"
                return user_id
            else:
                self.error_message = "用户名已存在"
                return None
        else:
            # 登录逻辑
            user_id = self.db.verify_login(self.username, self.password)
            if user_id:
                self.error_message = ""
                return user_id
            else:
                self.error_message = "用户名或密码错误"
                return None