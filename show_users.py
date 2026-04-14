from database import GameDatabase

def show_all_users():
    """显示数据库中的所有用户信息"""
    db = GameDatabase()
    cursor = db.conn.cursor()
    
    # 获取所有用户信息
    cursor.execute('''
        SELECT users.id, users.username, 
               MAX(game_records.score) as high_score,
               COUNT(game_records.id) as games_played
        FROM users 
        LEFT JOIN game_records ON users.id = game_records.user_id
        GROUP BY users.id, users.username
    ''')
    
    users = cursor.fetchall()
    
    if not users:
        print("\n数据库中还没有用户。")
        return
        
    print("\n当前注册用户列表:")
    print("-" * 50)
    print(f"{'ID':<6}{'用户名':<20}{'最高分':<10}{'游戏次数':<10}")
    print("-" * 50)
    
    for user_id, username, high_score, games_played in users:
        high_score = high_score if high_score is not None else 0
        games_played = games_played if games_played is not None else 0
        print(f"{user_id:<6}{username:<20}{high_score:<10}{games_played:<10}")
    
    print("-" * 50)

if __name__ == "__main__":
    show_all_users()