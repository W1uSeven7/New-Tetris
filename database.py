import os
import sqlite3
from datetime import datetime

# 获取当前文件所在目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 在当前目录下创建 data 文件夹存放数据库文件
DB_DIR = os.path.join(CURRENT_DIR, 'data')
DB_PATH = os.path.join(DB_DIR, 'tetris.db')

class GameDatabase:
    """
    游戏数据库类：负责处理所有与数据库相关的操作
    包括用户管理和游戏记录的存储与查询
    """
    def __init__(self):
        """
        初始化SQLite数据库连接
        数据库文件会自动在程序目录下创建
        """
        # 确保数据目录存在
        try:
            if not os.path.exists(DB_DIR):
                os.makedirs(DB_DIR)
        except Exception as e:
            print(f"创建数据库目录失败: {e}")
            raise
            
        # 建立数据库连接
        try:
            self.conn = sqlite3.connect(DB_PATH)
            # 启用外键约束
            self.conn.execute('PRAGMA foreign_keys = ON')
            self._create_tables()
        except Exception as e:
            print(f"数据库连接失败: {e}")
            raise

    def _create_tables(self):
        """
        创建数据库表结构
        包括用户表(users)和游戏记录表(game_records)
        """
        cursor = self.conn.cursor()
        
        # 用户表：存储用户信息
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 游戏记录表：存储每局游戏的记录
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            lines INTEGER NOT NULL,
            mode TEXT NOT NULL,
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        self.conn.commit()

    def add_user(self, username, password):
        """
        添加新用户
        返回:
            True: 添加成功
            False: 用户名已存在
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, password)
            )
            self.conn.commit()  # 立即提交更改
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        except Exception as e:
            print(f"添加用户时出错: {e}")
            return False

    def verify_user(self, username, password):
        """
        验证用户登录
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id FROM users WHERE username=? AND password=?',
            (username, password)
        )
        result = cursor.fetchone()
        return result[0] if result else None

    def verify_login(self, username, password):
        """验证登录"""
        cursor = self.conn.cursor()
        # 使用参数化查询防止SQL注入
        cursor.execute(
            'SELECT id, password FROM users WHERE username = ?',
            (username,)
        )
        result = cursor.fetchone()
        
        if result:
            stored_id, stored_password = result
            # 验证密码
            if stored_password == password:  # 实际应用中应该使用加密密码
                self.conn.commit()  # 确保所有更改都被保存
                return stored_id
        return None

    def add_game_record(self, user_id, score, lines, mode):
        """
        添加一条游戏记录
        """
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO game_records (user_id, score, lines, mode, played_at)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, score, lines, mode, datetime.now()))
        self.conn.commit()

    def get_high_scores(self, mode=None, user_id=None, limit=None):
        """
        获取高分榜
        参数:
            mode: 游戏模式
            user_id: 指定用户ID（可选）
            limit: 返回记录数量（可选，不指定则返回所有记录）
        """
        cursor = self.conn.cursor()
        query = '''
            SELECT users.username, MAX(game_records.score), game_records.lines
            FROM game_records
            JOIN users ON users.id = game_records.user_id
            WHERE 1=1
        '''
        params = []
        
        if mode:
            query += ' AND game_records.mode = ?'
            params.append(mode)
        
        if user_id:
            query += ' AND game_records.user_id = ?'
            params.append(user_id)
            
        query += ' GROUP BY users.username ORDER BY MAX(game_records.score) DESC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        cursor.execute(query, params)
        return cursor.fetchall()

    def check_username_exists(self, username):
        """检查用户名是否已存在"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        return cursor.fetchone() is not None

    def register_user(self, username, password):
        """
        注册新用户
        返回:
            user_id: 注册成功返回用户ID
            None: 注册失败（用户名已存在）
        """
        if self.check_username_exists(username):
            return None
            
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, password)
            )
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"注册用户时出错: {e}")
            return None

    def __del__(self):
        """
        确保程序结束时关闭数据库连接
        """
        if hasattr(self, 'conn'):
            try:
                self.conn.commit()
                self.conn.close()
            except Exception as e:
                print(f"关闭数据库连接失败: {e}")