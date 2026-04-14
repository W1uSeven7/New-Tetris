from database import GameDatabase

def init_database():
    """
    初始化数据库并添加测试用户
    """
    db = GameDatabase()
    
    # 添加测试用户
    test_users = [
        ("test", "123456"),
        ("admin", "admin"),
    ]
    
    for username, password in test_users:
        if db.add_user(username, password):
            print(f"成功添加用户: {username}")
        else:
            print(f"用户已存在: {username}")

if __name__ == "__main__":
    init_database()