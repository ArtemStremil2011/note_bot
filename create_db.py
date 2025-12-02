# reset_db.py
import sqlite3
import os

def reset_database(db_name):
    """Удаляет старую базу и создает новую с правильной структурой"""
    try:
        # Удаляем старый файл базы данных
        if os.path.exists(db_name):
            os.remove(db_name)
            print("✅ Старая база данных удалена")
        
        # Создаем новую базу с правильной структурой
        db = sqlite3.connect(db_name)
        cursor = db.cursor()
        
        # Создаем таблицу с 4 столбцами (без автоинкремента)
        cursor.execute("""
            CREATE TABLE users (
                user_id INTEGER,
                user_name TEXT,
                user_post_name TEXT,
                user_post_text TEXT
            )
        """)
        
        db.commit()
        db.close()
        print("✅ Новая база данных создана с правильной структурой")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    reset_database()