from database import create_tables
import sqlite3
from config import DATABASE_NAME
from config_database import data, data_additional


def check_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    try:
        tables = ['schedule', 'schedule_additional']
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                return False
        
        # Проверяем количество записей
        cursor.execute("SELECT COUNT(*) FROM schedule")
        db_count_main = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM schedule_additional")
        db_count_additional = cursor.fetchone()[0]
        
        if db_count_main != len(data) or db_count_additional != len(data_additional):
            return False
            
        # Проверяем хэши данных
        def get_table_hash(table_name, source_data):
            cursor.execute(f"SELECT GROUP_CONCAT(full_name||day_of_week||time_range||room||contact, '|') FROM {table_name}")
            db_hash = hash(cursor.fetchone()[0])
            data_hash = hash('|'.join([''.join(map(str, item)) for item in source_data]))
            return db_hash == data_hash
        
        return get_table_hash('schedule', data) and get_table_hash('schedule_additional', data_additional)
        
    except sqlite3.Error as e:
        print(f"Ошибка проверки БД: {e}")
        return False
    finally:
        conn.close()

def update_database():
    """Полная перезапись данных в БД"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DROP TABLE IF EXISTS schedule")
        cursor.execute("DROP TABLE IF EXISTS schedule_additional")
        
        create_tables()
        
        # Вставляем данные
        cursor.executemany(
            '''INSERT INTO schedule 
            (full_name, day_of_week, time_range, room, contact) 
            VALUES (?, ?, ?, ?, ?)''',
            data
        )
        
        cursor.executemany(
            '''INSERT INTO schedule_additional 
            (full_name, day_of_week, time_range, room, contact) 
            VALUES (?, ?, ?, ?, ?)''',
            data_additional
        )
        
        conn.commit()
        print(f"Обновлено записей: {len(data) + len(data_additional)}")
        return True
        
    except sqlite3.Error as e:
        print(f"Ошибка обновления БД: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    if update_database():
        print("✅ База данных успешно заполнена!")